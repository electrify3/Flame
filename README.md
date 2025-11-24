Flame
=====

**Flame** is a versatile, self-hosted Discord bot built for server management and community engagement. It supports both prefix (`??`) and slash (`/`) commands and even no prefix, with features spanning moderation, logging, role management,points system (useful in coducting tournaments), music playback, utilities, and fun commands.

Modules
--------

*   **Moderation**: Contains typical moderation commands but enhanced and with better controlls.
*   **Logging**: Send Logs (Member join, ban, update, message delete etc).
*   **Roles**: Role Commands with Bulk-assign or remove features.
*   **Points**: Its a points system design to tournaments, players can get points on winning but lose on loosing.
*   **Music**: It supports YT streaming. 
*   **Tools**: Contain commads such as channel lock/unlock, slowmode setup.
*   **Fun**: Fun commands such as gifs, Truth and Dare and much more.
*   **Voice**: Commands supporting voice channel and members moderation.
*   **Misc**: Misc commands such as userinfo, avatar, .

Requirements
--------------------

**Python 3.12+**  
**Java 24.0+** (if hosting a local lavalink server)  
**ffmpeg 7.1+** (Again its optional, install if you're using `extras/music [ffmpeg].py`)

Setup
--------------------
### 1. Installing all the requirements.  

```
pip install -r requirements.txt
```

### 2. Setup ENV file
```
TOKEN=Your_discord_bot_token_here
TENOR=Your_tenor_api_key_here
```
**Note:** Tenor key is only required for gif commands.

### Setting Up Lavalink Server [Optional]
See [Lavalink](https://github.com/lavalink-devs/Lavalink) to setup your own server.  
youtube-plugin is required too in the server.  

Use these `application.yml` file in your lavalink server:
```yml
server: # REST and WS server
  port: 8080
  address: 127.0.0.1
  http2:
    enabled: false # Whether to enable HTTP/2 support
plugins:
  youtube:
    enabled: true # Whether this source can be used.
    allowSearch: true # Whether "ytsearch:" and "ytmsearch:" can be used.
    allowDirectVideoIds: true # Whether just video IDs can match. If false, only complete URLs will be loaded.
    allowDirectPlaylistIds: true # Whether just playlist IDs can match. If false, only complete URLs will be loaded.
    # The clients to use for track loading. See below for a list of valid clients.
    # Clients are queried in the order they are given (so the first client is queried first and so on...)
    clients:
      - MUSIC
      - ANDROID_VR
      - WEB
      - WEBEMBEDDED 
#  name: # Name of the plugin
#    some_key: some_value # Some key-value pair for the plugin
#    another_key: another_value
lavalink:
  plugins:
    -dependency: "dev.lavalink.youtube:youtube-plugin:1.13.4"
    snapshot: false
  server:
    password: "password"
    sources:
      youtube: false
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      nico: true
      http: true # warning: keeping HTTP enabled without a proxy configured could expose your server's IP address.
      local: false
    filters: # All filters are enabled by default
      volume: true
      equalizer: true
      karaoke: true
      timescale: true
      tremolo: true
      vibrato: true
      distortion: true
      rotation: true
      channelMix: true
      lowPass: true
    nonAllocatingFrameBuffer: false # Setting to true reduces the number of allocations made by each player at the expense of frame rebuilding (e.g. non-instantaneous volume changes)
    bufferDurationMs: 400 # The duration of the NAS buffer. Higher values fare better against longer GC pauses. Duration <= 0 to disable JDA-NAS. Minimum of 40ms, lower values may introduce pauses.
    frameBufferDurationMs: 5000 # How many milliseconds of audio to keep buffered
    opusEncodingQuality: 10 # Opus encoder quality. Valid values range from 0 to 10, where 10 is best quality but is the most expensive on the CPU.
    resamplingQuality: LOW # Quality of resampling operations. Valid values are LOW, MEDIUM and HIGH, where HIGH uses the most CPU.
    trackStuckThresholdMs: 10000 # The threshold for how long a track can be stuck. A track is stuck if does not return any audio data.
    useSeekGhosting: true # Seek ghosting is the effect where whilst a seek is in progress, the audio buffer is read from until empty, or until seek is ready.
    youtubePlaylistLoadLimit: 6 # Number of pages at 100 each
    playerUpdateInterval: 5 # How frequently to send player updates to clients, in seconds
    youtubeSearchEnabled: true
    soundcloudSearchEnabled: true
    gc-warnings: true

    timeouts:
      connectTimeoutMs: 3000
      connectionRequestTimeoutMs: 3000
      socketTimeoutMs: 3000

metrics:
  prometheus:
    enabled: false
    endpoint: /metrics

sentry:
  dsn: ""
  environment: ""

logging:
  file:
    path: ./logs/

  level:
    root: INFO
    lavalink: INFO

  request:
    enabled: true
    includeClientInfo: true
    includeHeaders: false
    includeQueryString: true
    includePayload: true
    maxPayloadLength: 10000


  logback:
    rollingpolicy:
      max-file-size: 1GB
      max-history: 30
```
