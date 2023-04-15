# Tandem video builder

### The purpose of this tool is to apply a clip recorded with a GOPRO or similar to a predefined template. This is done in particular with tandem flying experience, where at the end of each flight, a clip is made available and eventually provided on a branded template to the customer. Due to speed reason, I generate this script in order to deal with it as fast as possible.

First have to install ffmpeg on host server. On M2 silicon I switch the codec in app.py, line number 81. For M2 silicon I use h264_videotoolbox instead of libx264

Second I need ImageMagick by installing sudo apt install libmagick++-dev and then going to change:

```sudo vim /etc/ImageMagick-6/policy.xml ``` and then comment the @ policy by change from ```<policy domain="path" rights="none" pattern="@*" />``` to ```<!--<policy domain="path" rights="none" pattern="@*" /> -->```

To run Streamlit:
`streamlit run webapp.py`

Tu run just the script
```python app.py```

The python scripts expects:
header, template and closing in the output folder in mp4 format.

clip.mp4, which is your clip can stay in the root.

# To run as a docker
```
docker build -t tandem_video .
docker run -v "$(pwd)":/app/output tandem_video -f clip_short.mp4 -n Test -d 10/08/1977 -l Salamanca -v 0.3

docker run -v "$(pwd)":/app/output -v "$(pwd)"/config.ini:/app/config.ini tandem_video -f clip_short.mp4 -n Test -d 10/08/1977 -l Salamanca -v 0.3
```

# To push to docker hub
```
docker tag tandem_video simseve/tandem-video:1.0
docker push simseve/tandem-video:1.0
```

# To pull from docker 
`docker pull simseve/tandem-video:1.0`


# To run from VSCode
## To bypass all the switches simply set
`export TEST_MODE=1`
## then run the following script or from VSC
`python app.py `

## alternatively run
`python app.py  -f clip_short.mp4 -n Simone -d 23/4/2023 -l Bergeggi`

## You can also use email and volume as a optional switches
`python app.py  -f clip_short.mp4 -n Simone -d 23/4/2023 -l Bergeggi -v 0.3 -e simone.severini.simone@icloud.com`