import unittest
from pythonGraphicalManipulator import *

class TestImageManipulationMethods(unittest.TestCase):
    def setUp(self):
        self.pixel_grid = [
            [(255, 0, 0), (0, 255, 0), (0, 0, 255)],  # Red, Green, Blue
            [(255, 255, 0), (0, 255, 255), (255, 0, 255)],  # Yellow, Cyan, Magenta
            [(128, 128, 128), (192, 192, 192), (64, 64, 64)]  # Gray shades
        ]
        self.target_color = (255, 0, 0)  # Red color
        self.replacement_color = (0, 255, 0)  # Green color

    def test_imageToPixelGrid(self):
        image_path = 'testInputImage.jpg'
        pixel_grid = imageToPixelGrid(image_path)
        self.assertIsInstance(pixel_grid, list)
        self.assertGreater(len(pixel_grid), 0)

    def test_pixelGridToImage(self):
        output_image_path = 'testOutputImage.jpg'
        pixel_grid = self.pixel_grid
        pixelGridToImage(pixel_grid, output_image_path)
        try:
            with open(output_image_path, 'r'):
                file_exists = True
        except FileNotFoundError:
            file_exists = False
        self.assertTrue(file_exists)

    def test_resizeImage(self):
        resized_pixel_grid = resizeImage(self.pixel_grid, 5, 5)
        self.assertEqual(len(resized_pixel_grid), 5)
        self.assertEqual(len(resized_pixel_grid[0]), 5)

    def test_cropImage(self):
        cropped_pixel_grid = cropImage(self.pixel_grid, 0, 0, 1, 1)
        self.assertEqual(len(cropped_pixel_grid), 2) 
        self.assertEqual(len(cropped_pixel_grid[0]), 2) 

    def test_flipHoriz(self):
        flipped_pixel_grid = flipHoriz(self.pixel_grid)
        self.assertEqual(flipped_pixel_grid[0][0], self.pixel_grid[0][-1]) 

    def test_flipVert(self):
        flipped_pixel_grid = flipVert(self.pixel_grid)
        self.assertEqual(flipped_pixel_grid[0][0], self.pixel_grid[-1][0])

    def test_bnw(self):
        bnw_pixel_grid = bnw(self.pixel_grid)
        self.assertEqual(bnw_pixel_grid[0][0], (85, 85, 85))

    def test_singleColorPop(self):
        result_pixel_grid = singleColorPop(self.pixel_grid, *self.target_color)
        self.assertEqual(result_pixel_grid[0][0], self.target_color) 
        self.assertEqual(result_pixel_grid[0][1], (85, 85, 85)) 

    def test_singleColorRemove(self):
        result_pixel_grid = singleColorRemove(self.pixel_grid, *self.target_color)
        self.assertEqual(result_pixel_grid[0][0], (85, 85, 85))
        self.assertEqual(result_pixel_grid[0][1], (0, 255, 0)) 

    def test_changeColor(self):
        result_pixel_grid = changeColor(self.pixel_grid, *self.target_color, *self.replacement_color)
        self.assertEqual(result_pixel_grid[0][0], self.replacement_color) 
        self.assertEqual(result_pixel_grid[0][1], (0, 255, 0)) 

    def test_adjustBrightness(self):
        result_pixel_grid = adjustBrightness(self.pixel_grid, 1.5)
        self.assertEqual(result_pixel_grid[0][0], (255, 0, 0)) 
        self.assertEqual(result_pixel_grid[1][1], (255, 255, 255)) 

    def test_adjustShadowIntensity(self):
        result_pixel_grid = adjustShadowIntensity(self.pixel_grid, 0.5)
        self.assertEqual(result_pixel_grid[2][2], (32, 32, 32))

    def test_adjustBlackPoint(self):
        result_pixel_grid = adjustBlackPoint(self.pixel_grid, 50)
        self.assertEqual(result_pixel_grid[2][2], (14, 14, 14))

    def test_adjustWarmth(self):
        result_pixel_grid = adjustWarmth(self.pixel_grid, 1.2)
        self.assertEqual(result_pixel_grid[0][0], (255, 0, 0)) 
        self.assertEqual(result_pixel_grid[1][1], (255, 255, 0)) 

if __name__ == '__main__':
    unittest.main()