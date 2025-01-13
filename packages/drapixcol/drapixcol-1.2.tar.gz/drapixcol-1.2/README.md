# Drapixcol
Python library for drawing with pixels.  
<br />
<br />
The `create_canvas` function creates a canvas with a given width and color, example:  
```python
width, height = 10, 20
canvas = create_canvas(width, height, white)
```  
This code created an opaque canvas with a width of 10, a height of 20, and a white color,  
Also, this function can be passed transparency as the fourth argument.  
<br />
The `pixel` function paints a specific pixel a color, example:  
```python
pixel(canvas, 5, 0 , black)
```  
This code paints a pixel on the canvas "canvas" at coordinates x=5 y=0 black,  
You can also pass transparency to this function as the fifth argument.  
<br />
The `repeat` function draws a sequence of pixels in any direction and with any space between pixels, example:
```python
repeat(canvas, 10, 5, 10, forward, black)
```  
This code draws a sequence of pixels on the canvas "canvas" 10 times starting at coordinate x=5 y=10 moving forward, the pixel color is black,  
You can also pass transparency as the seventh argument and the distance between pixels as the eighth argument.  
<br />
The ``save_canvas`` function saves the canvas at a specific size, example:  
```python
save_canvas(canvas, in100times)
```  
This code saves the canvas "canvas" by making it 100 times bigger.  
<br />
<br />
Here are all the arguments that can be passed to functions:  
<br />
Colors:  
```
black  
white  
red  
blue  
yellow  
green  
brown  
sky_blue  
light_sky_blue  
violet  
grey  
orange  
pink  
light_green  
dark_red  
null  
```
You can also create your own colors as all colors are stored in RGBA format.  
<br />
Transparency:  
```
translucent 
transparent  
on80  
on60  
on40  
on20  
opaque
```  
You can also create your own transparency since all colors are stored in RGBA format.  
<br />
Directions:  
```
forward  
down  
back  
up  
down_right  
up_right  
down_left  
up_left
```
<br />

Enlargement:  
```
in2times  
in5times  
in10times  
in50times  
in100times  
in200times
in500times  
in1000times
``` 
You can also create your own magnification.
