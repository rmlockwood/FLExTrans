# FTtranslator without FieldWorks, for Linux hosts such as Railway.
#
# Build from Dev\FTtranslator (the build context must hold fttranslator/, hcparse/, hcsynth/, web/ and deploy/bundle/):
#   docker build -t fttranslator .
# Railway finds this file by its name when the service's Root Directory is /Dev/FTtranslator, and builds it the same way from git. deploy/bundle is a copy of a work project's
# Output\ftt_bundle, made on the desktop with export-bundle. It is committed for the FTT-Scratch test pair only: it holds the project's lexicon, so real projects' bundles are sent to the
# running server with upload-bundle instead, and kept on a volume (see the end of this file).
#
# Three stages: the .NET 8 HermitCrab parser and synthesizer are built with the .NET SDK, the React page with Node, and the final image has only the .NET runtime, Python, the Apertium tools
# and the built pieces. The server listens on $PORT (Railway sets it). It asks for the password in the FTT_PASSWORD environment variable, set in the Railway service's Variables, and
# refuses to start without one since it listens on 0.0.0.0 (see SAFETY in fttranslator/offlineserver.py).

# 1. The HermitCrab parser (hcparse) and synthesizer (hcsynth), both pinned to SIL.Machine 3.9.5 in their project files
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS dotnet
WORKDIR /src
COPY hcsynth/ hcsynth/
COPY hcparse/ hcparse/
RUN dotnet publish hcsynth/HCSynthByGloss.Net8.csproj -c Release -o /out/hcsynth \
 && dotnet publish hcparse/HCParse.Net8.csproj -c Release -o /out/hcparse

# 2. The React front end
FROM node:20-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# 3. The server: .NET 8 runtime (Debian 12), plus Python and Debian's Apertium tools. Debian's lttoolbox has only lt-proc; lt-comp, which compiles the bilingual lexicon, is in lttoolbox-dev.
# pythonnet lets the server load HCSynthByGloss.dll once (--hcsynth-dll) instead of starting it for every text. Debian marks its Python as externally managed, hence --break-system-packages;
# nothing else in the image uses pip.
FROM mcr.microsoft.com/dotnet/runtime:8.0
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip apertium lttoolbox lttoolbox-dev \
 && pip3 install --no-cache-dir --break-system-packages pythonnet==3.0.5 \
 && rm -rf /var/lib/apt/lists/*

# Fail the build, not the first translation, if a tool transfer.py runs is missing
RUN for tool in lt-comp lt-proc apertium-preprocess-transfer apertium-transfer apertium-interchunk apertium-postchunk; do command -v $tool || { echo "missing: $tool"; exit 1; }; done

WORKDIR /app
COPY --from=dotnet /out/hcparse /opt/hcparse
COPY --from=dotnet /out/hcsynth /opt/hcsynth
COPY --from=web /web/dist web/dist
COPY fttranslator/ fttranslator/
COPY deploy/bundle/ /app/bundle/

# Fail the build, not the server's start, if pythonnet can't load the synthesis DLL on .NET 8
ENV DOTNET_ROOT=/usr/share/dotnet
RUN python3 -c "import sys, pythonnet; pythonnet.load('coreclr', runtime_config='/opt/hcsynth/HCSynthByGloss.runtimeconfig.json'); sys.path.append('/opt/hcsynth'); import clr; clr.AddReference('/opt/hcsynth/HCSynthByGloss.dll'); from SIL.HCSynthByGloss import HCSynthByGlossDll; print('pythonnet OK')"

# The bundles live on a Railway volume mounted at /data, so uploaded ones (upload-bundle) survive redeploys; without a volume /data/bundles is in the container and is lost on each deploy.
# deploy/bundle (FTT-Scratch) is seeded into it at start-up unless a bundle of that name is already there. See SEVERAL BUNDLES in fttranslator/offlineserver.py.
ENV PORT=8080 PYTHONUNBUFFERED=1 FTT_BUNDLES=/data/bundles
EXPOSE 8080
CMD python3 -m fttranslator serve-offline --bundles "$FTT_BUNDLES" --seed /app/bundle --hcparse "dotnet /opt/hcparse/HCParse.dll" --hcsynth-dll /opt/hcsynth/HCSynthByGloss.dll --host 0.0.0.0 --port "$PORT"
