# FTtranslator without FieldWorks, for Linux hosts such as Railway.
#
# Build from Dev\FTtranslator (the build context must hold fttranslator/, hcparse/, hcsynth/, web/ and deploy/bundle/):
#   docker build -t fttranslator .
# Railway finds this file by its name when the service's Root Directory is /Dev/FTtranslator, and builds it the same way from git. deploy/bundle is a copy of a work project's
# Output\ftt_bundle, made on the desktop with export-bundle. It is committed for the FTT-Scratch test pair only: it holds the project's lexicon, so a real project's bundle needs another way in.
#
# Three stages: the .NET 8 HermitCrab parser and synthesizer are built with the .NET SDK, the React page with Node, and the final image has only the .NET runtime, Python, the Apertium tools
# and the built pieces. The server listens on $PORT (Railway sets it).

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
FROM mcr.microsoft.com/dotnet/runtime:8.0
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 apertium lttoolbox lttoolbox-dev \
 && rm -rf /var/lib/apt/lists/*

# Fail the build, not the first translation, if a tool transfer.py runs is missing
RUN for tool in lt-comp lt-proc apertium-preprocess-transfer apertium-transfer apertium-interchunk apertium-postchunk; do command -v $tool || { echo "missing: $tool"; exit 1; }; done

WORKDIR /app
COPY --from=dotnet /out/hcparse /opt/hcparse
COPY --from=dotnet /out/hcsynth /opt/hcsynth
COPY --from=web /web/dist web/dist
COPY fttranslator/ fttranslator/
COPY deploy/bundle/ /app/bundle/

ENV PORT=8080 PYTHONUNBUFFERED=1
EXPOSE 8080
CMD python3 -m fttranslator serve-offline --bundle /app/bundle --hcparse "dotnet /opt/hcparse/HCParse.dll" --hcsynth "dotnet /opt/hcsynth/HCSynthByGloss.dll" --host 0.0.0.0 --port "$PORT"
