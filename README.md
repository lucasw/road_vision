# road_vision
Find features in vehicle mounted camera video

Turn video into image sequence (later process video)

Crop images

convert image.jpg -crop 1920x880+0+0 +repage image2.jpg
for i in *jpg; do convert $i -crop 1920x880+0+0 +repage ../$i; done
