class NoneProcessor:
    def __init__(self):
        pass

    @staticmethod
    def get_name():
        return "None"

    @staticmethod
    def get_parameter_list():
        return []

    @staticmethod
    def evaluate(img, circles, parameters):
        return []

    # @staticmethod
    # def update_result_image(img, active_image_area, circles, results : list[int], draw_parameters):
    #     pass
