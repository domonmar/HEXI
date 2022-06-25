import PIL
import PIL.ImageDraw
import PIL.ImageFont

def rect_around(x, y, size, offset_x, offset_y):
    x1 = int(x) - int(size) + int(offset_x)
    y1 = int(y) - int(size) + int(offset_y)
    x2 = int(x) + int(size) + int(offset_x)
    y2 = int(y) + int(size) + int(offset_y)
    return [x1, y1, x2, y2]

def draw_circles_on_image(img, active_image_area, circles, draw_perimeters, circle_classes = None, circle_class_colors = [(255, 0, 0), (0, 255, 0)]):
    result_image = img

    if len(circles) > 0:
        # draw cirlces on image:
        draw = PIL.ImageDraw.Draw(result_image)

        offset_x, offset_y, dummy1, dummy2 = active_image_area

        for index, circle in enumerate(circles):
            circle_class = circle_classes[index] if circle_classes is not None else 0
            color = circle_class_colors[circle_class]
            center_x = circle[0]
            center_y = circle[1]
            radius = circle[2]
            if draw_perimeters:
                # draw the outer circle
                draw.ellipse(rect_around(center_x, center_y, radius, offset_x,
                                              offset_y), fill=None, outline=color, width=1)
            # draw the center of the circle
            center_point_size = 1
            draw.rectangle(rect_around(center_x, center_y, center_point_size,
                                       offset_x, offset_y), fill=color, outline=None, width=1)

def draw_info_text_on_image(img, info_text):
    draw = PIL.ImageDraw.Draw(img)

    font = PIL.ImageFont.truetype("cour.ttf", 20)
    text_size = draw.multiline_textsize(info_text, font=font)

    padding = 5

    pos_x = padding
    pos_y = img.height - text_size[1] - padding

    draw.rectangle([0, pos_y - padding, text_size[0] + padding + padding,
                    img.height], fill=(255, 255, 255), outline=None, width=1)
    draw.multiline_text((pos_x, pos_y), info_text, font=font, fill=(0, 0, 0))