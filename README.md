# road_vision
Find features in vehicle mounted camera video

Turn video into image sequence (later process video)

ffmpeg

Crop images

`
convert image.jpg -crop 1920x880+0+0 +repage image2.jpg
for i in *jpg; do convert $i -crop 1920x880+0+0 +repage ../$i; done
`

Look at SPD video later - a few examples are online for hackathon.
Cameras look to be 640x480, though probably have decent nightvision.
Videos are more likely to contain driving outside of lines.
Is there video of just driving down the road, no sirens, not going to an incident?
