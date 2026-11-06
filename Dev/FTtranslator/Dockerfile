# FTtranslator without FieldWorks, for Linux hosts such as Railway.
#
# Build from Dev\FTtranslator (the build context must hold fttranslator/, hcparse/, hcsynth/, apertium/, web/ and deploy/bundle/):
#   docker build -t fttranslator .
# Railway finds this file by its name when the service's Root Directory is /Dev/FTtranslator, and builds it the same way from git. deploy/bundle is a copy of a work project's
# Output\ftt_bundle, made on the desktop with export-bundle. It is committed for the FTT-Scratch test pair only: it holds the project's lexicon, so real projects' bundles are sent to the
# running server with upload-bundle instead, and kept on a volume (see the end of this file).
#
# Three stages: the .NET 8 HermitCrab parser and synthesizer and FTApertium (the C# port of the Apertium tools, see apertium/README.md) are built with the .NET SDK, the React page with Node,
# and the final image has only the .NET runtime, Python and the built pieces; no Apertium packages are needed. The server listens on $PORT (Railway sets it). It asks for the password in the FTT_PASSWORD environment variable, set in the Railway service's Variables, and
# refuses to start without one since it listens on 0.0.0.0 (see SAFETY in fttranslator/offlineserver.py).

# 1. The HermitCrab parser (hcparse) and synthesizer (hcsynth), both pinned to SIL.Machine 3.9.5 in their project files, and FTApertium, the transfer step
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS dotnet
WORKDIR /src
COPY hcsynth/ hcsynth/
COPY hcparse/ hcparse/
COPY apertium/ apertium/
RUN dotnet publish hcsynth/HCSynthByGloss.Net8.csproj -c Release -o /out/hcsynth \
 && dotnet publish hcparse/HCParse.Net8.csproj -c Release -o /out/hcparse \
 && dotnet publish apertium/FTApertium.csproj -c Release -o /out/apertium

# 2. The React front end
FROM node:20-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# 3. The server: .NET 8 runtime (Debian 12) plus Python. pythonnet lets the server load FTtranslator.Apertium.dll (--apertium-dll) and HCSynthByGloss.dll (--hcsynth-dll) once instead of
# starting programs for every text, and regex is the module FLExTrans applies Text Out rules with (see fttranslator/textout.py). Debian marks its Python as externally managed, hence
# --break-system-packages; nothing else in the image uses pip. (Before FTApertium the image installed Debian's apertium, lttoolbox and lttoolbox-dev; serve-offline --apertium-tools would
# need them again.)
FROM mcr.microsoft.com/dotnet/runtime:8.0
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip \
 && pip3 install --no-cache-dir --break-system-packages pythonnet==3.0.5 regex==2026.2.28 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=dotnet /out/hcparse /opt/hcparse
COPY --from=dotnet /out/hcsynth /opt/hcsynth
COPY --from=dotnet /out/apertium /opt/apertium
COPY --from=web /web/dist web/dist
COPY fttranslator/ fttranslator/
COPY deploy/bundle/ /app/bundle/

# Fail the build, not the server's start, if pythonnet can't load the transfer and synthesis DLLs on .NET 8 (in one process, as the server does) or the Text Out rules can't be imported
ENV DOTNET_ROOT=/usr/share/dotnet
RUN python3 -c "import fttranslator.textout; print('textout OK')"
RUN python3 -c "from fttranslator.dotnet import startDotNet; startDotNet('/opt/apertium/FTtranslator.Apertium.dll', 'FTApertium'); startDotNet('/opt/hcsynth/HCSynthByGloss.dll', 'HCSynthByGloss'); import clr; clr.AddReference('/opt/apertium/FTtranslator.Apertium.dll'); clr.AddReference('/opt/hcsynth/HCSynthByGloss.dll'); from FTtranslator.Apertium import ApertiumTransfer; from SIL.HCSynthByGloss import HCSynthByGlossDll; print('pythonnet OK')"

# The bundles live on a Railway volume mounted at /data, so uploaded ones (upload-bundle) survive redeploys; without a volume /data/bundles is in the container and is lost on each deploy.
# deploy/bundle (FTT-Scratch) is seeded into it at start-up unless a bundle of that name is already there. See SEVERAL BUNDLES in fttranslator/offlineserver.py.
ENV PORT=8080 PYTHONUNBUFFERED=1 FTT_BUNDLES=/data/bundles
EXPOSE 8080
# exec makes Python PID 1, so the stop signal (docker stop, a Railway redeploy) reaches the server instead of the shell; the shell form is kept so $PORT is expanded
CMD exec python3 -m fttranslator serve-offline --bundles "$FTT_BUNDLES" --seed /app/bundle --hcparse "dotnet /opt/hcparse/HCParse.dll" --apertium-dll /opt/apertium/FTtranslator.Apertium.dll --hcsynth-dll /opt/hcsynth/HCSynthByGloss.dll --host 0.0.0.0 --port "$PORT"
