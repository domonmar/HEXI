import cv2


def process_image(img, detector, detector_parameters, processor, processor_parameters):
    circles = detector.evaluate(img, detector_parameters)
    circle_classification = processor.evaluate(img, circles, processor_parameters)

    return circles, circle_classification


def overlay_circles(img, circles, circle_classification, draw_perimeters):
    image_with_circles = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    circle_class_colors = [(0, 0, 255), (0, 255, 0)]
    for index, circle in enumerate(circles):
        circle_type = circle_classification[index]
        color = circle_class_colors[circle_type]
        radius = circle[2]
        if draw_perimeters:
            # draw the outer circle
            cv2.circle(image_with_circles, (circle[0], circle[1]), circle[2], color, 1)
        # draw the center of the circle
        center_point_size = 3 if radius >= 10 else 1
        cv2.circle(image_with_circles, (circle[0], circle[1]), 2, color, center_point_size)
    return image_with_circles


def process_image_and_show(image_path, edge_detect_threshold, circle_threshold, radius, loose_circle_threshold=1.2):
    img = cv2.imread(image_path, 0)
    circles, circle_classification = process_image(
        img, edge_detect_threshold, circle_threshold, radius, loose_circle_threshold)
    img_processed = overlay_circles(img, circles, circle_classification)
    cv2.imshow(image_path + ': circle classification', img_processed)
