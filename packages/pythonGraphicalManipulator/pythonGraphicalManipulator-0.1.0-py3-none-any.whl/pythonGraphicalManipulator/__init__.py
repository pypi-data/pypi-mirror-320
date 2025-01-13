from PIL import Image


# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

def imageToPixelGrid(imagePath, outputToTextFile=False, textFile=None):
    """
    Converts an image into a pixel grid (2D array of RGB tuples).
    Optionally, writes the pixel grid to a text file.

    :param imagePath: Path to the input image.
    :param outputToTextFile: Boolean indicating whether to write the grid to a file.
    :param textFile: Path to the text file (required if outputToTextFile is True).
    :return: Pixel grid or written file.
    """
    image = Image.open(imagePath)
    image = image.convert("RGB")
    width, height = image.size
    pixelGrid = []
    # Loop through each pixel in the image and get the RGB value
    for y in range(height):
        row = []  # A new row for each height level
        for x in range(width):
            pixel = image.getpixel((x, y))  # RGB value at (x, y)
            row.append(pixel)
        pixelGrid.append(row)
    if(outputToTextFile):
        if(textFile is None): raise ValueError("Output to text file set to True, but no text file specified for output")
        file = open(textFile, "w")
        file.write(pixelGrid)
        file.close()
        return file
    return pixelGrid

def pixelGridToImage(pixelGrid, outputImagePath):
    """
    Converts a pixel grid back to an image and saves it.

    :param pixelGrid: 2D array of RGB tuples.
    :param outputImagePath: Path to save the output image.
    """
    height = len(pixelGrid)
    width = len(pixelGrid[0]) if height > 0 else 0
    image = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), pixelGrid[y][x])
    return image.save(outputImagePath)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

def resizeImage(pixelGrid, length, width):
    """
    Resizes the pixel grid to specified dimensions.

    :param pixelGrid: 2D array of RGB tuples.
    :param length: New height of the image.
    :param width: New width of the image.
    :return: Resized pixel grid.
    """
    image = Image.new("RGB", (len(pixelGrid[0]), len(pixelGrid)))
    for y in range(len(pixelGrid)):
        for x in range(len(pixelGrid[0])):
            image.putpixel((x, y), pixelGrid[y][x])
    resizedImage = image.resize((width, length), Image.Resampling.LANCZOS)
    resizedPixelGrid = [
        [resizedImage.getpixel((x, y)) for x in range(resizedImage.width)]
        for y in range(resizedImage.height)
    ]
    return resizedPixelGrid

def cropImage(pixelGrid, top, left, right, bottom):
    """
    Crops the pixel grid to specified dimensions.

    :param pixelGrid: 2D array of RGB tuples.
    :param top: Number of rows to remove from the top.
    :param left: Number of columns to remove from the left.
    :param right: Number of columns to remove from the right.
    :param bottom: Number of rows to remove from the bottom.
    :return: Cropped pixel grid.
    """
    height = len(pixelGrid)
    width = len(pixelGrid[0])
    croppedPixelGrid=[
        row[left : width - right]
        for row in pixelGrid[top : height - bottom]
    ]
    return croppedPixelGrid

# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

def flipHoriz(pixelGrid):
    """
    Flips the pixel grid horizontally.

    :param pixelGrid: 2D array of RGB tuples.
    :return: Horizontally flipped pixel grid.
    """
    return [row[::-1] for row in pixelGrid]

def flipVert(pixelGrid):
    """
    Flips the pixel grid vertically.

    :param pixelGrid: 2D array of RGB tuples.
    :return: Vertically flipped pixel grid.
    """
    return pixelGrid[::-1]

# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

def bnw(pixelGrid):
    """
    Converts the pixel grid to black and white.

    :param pixelGrid: 2D array of RGB tuples.
    :return: Black and white pixel grid.
    """
    bnwGrid = []
    for row in pixelGrid:
        bnwRow = []
        for r, g, b in row:
            average = int((r + g + b) / 3)
            bnwRow.append((average, average, average))
        bnwGrid.append(bnwRow)
    return bnwGrid

def singleColorPop(pixelGrid, r, g, b, threshold=50):
    """
    Pops a single color by retaining pixels close to the specified color and grayscaling others.

    :param pixelGrid: 2D array of RGB tuples.
    :param r: Red component of the target color.
    :param g: Green component of the target color.
    :param b: Blue component of the target color.
    :param threshold: Maximum distance for color matching.
    :return: Color-popped pixel grid.
    """
    def colorDistance(c1, c2): return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5
    target = (r, g, b)
    popGrid = []
    for row in pixelGrid:
        popRow = []
        for pixel in row:
            distance = colorDistance(pixel, target)
            if distance < threshold:
                popRow.append(pixel) 
            else:
                avg = int((pixel[0] + pixel[1] + pixel[2]) / 3)
                popRow.append((avg, avg, avg)) 
        popGrid.append(popRow)
    return popGrid

def singleColorRemove(pixelGrid, r, g, b, threshold=50):
    """
    Removes a single color by grayscaling pixels close to the specified color.

    :param pixelGrid: 2D array of RGB tuples.
    :param r: Red component of the target color.
    :param g: Green component of the target color.
    :param b: Blue component of the target color.
    :param threshold: Maximum distance for color matching.
    :return: Color-removed pixel grid.
    """
    def colorDistance(c1, c2): return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5
    target = (r, g, b)
    removeGrid = []
    for row in pixelGrid:
        removeRow = []
        for pixel in row:
            distance = colorDistance(pixel, target)
            if distance < threshold:
                avg = int((pixel[0] + pixel[1] + pixel[2]) / 3)
                removeRow.append((avg, avg, avg))
            else:
                removeRow.append(pixel)
        removeGrid.append(removeRow)
    return removeGrid

def changeColor(pixelGrid, r1, g1, b1, r2, g2, b2, threshold=0):
    """
    Changes all occurrences of a target color to a replacement color.

    :param pixelGrid: 2D array of RGB tuples.
    :param r1, g1, b1: Target color components.
    :param r2, g2, b2: Replacement color components.
    :param threshold: Maximum distance for color matching.
    :return: Pixel grid with color replaced.
    """
    def colorDistance(c1, c2): return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5
    target = (r1, g1, b1)
    replacement = (r2, g2, b2)
    modifiedGrid = []
    for row in pixelGrid:
        modifiedRow = []
        for pixel in row:
            if colorDistance(pixel, target) <= threshold: modifiedRow.append(replacement)
            else: modifiedRow.append(pixel)
        modifiedGrid.append(modifiedRow)
    return modifiedGrid

# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

def adjustShadowIntensity(pixelGrid, factor):
    """
    Adjusts shadow intensity by modifying darker pixels.
    Positive factor darkens, negative factor lightens.

    :param pixelGrid: 2D array of RGB tuples.
    :param factor: Adjustment factor (>0 to darken, <0 to lighten).
    :return: Shadow-intensity-adjusted pixel grid.
    """
    def adjust(pixel): return tuple(int(c * factor if c < 128 else c) for c in pixel)
    return [[adjust(pixel) for pixel in row] for row in pixelGrid]

def adjustBlackPoint(pixelGrid, level):
    """
    Adjusts the black point of the image.
    Positive level increases darkness, negative level decreases it.

    :param pixelGrid: 2D array of RGB tuples.
    :param level: Adjustment level (>0 to darken, <0 to lighten).
    :return: Black-point-adjusted pixel grid.
    """
    def adjust(pixel): return tuple(max(c - level, 0) for c in pixel)
    return [[adjust(pixel) for pixel in row] for row in pixelGrid]

def adjustBrightness(pixel_grid, brightness_factor):
    """
    Adjusts the brightness of the image.
    Positive factor increases brightness, negative factor decreases it.

    :param pixelGrid: 2D array of RGB tuples.
    :param factor: Adjustment factor (>0 to brighten, <0 to darken).
    :return: Brightness-adjusted pixel grid.
    """
    adjusted_pixel_grid = []
    for row in pixel_grid:
        adjusted_row = []
        for pixel in row:
            r, g, b = pixel
            r = min(max(0, int(r * brightness_factor)), 255)
            g = min(max(0, int(g * brightness_factor)), 255)
            b = min(max(0, int(b * brightness_factor)), 255)
            adjusted_row.append((r, g, b))
        adjusted_pixel_grid.append(adjusted_row)
    return adjusted_pixel_grid

def adjustWarmth(pixel_grid, warmth_factor):
    """
    Adjusts the warmth of the image.
    Positive factor increases red/yellow tones, negative factor increases blue tones.

    :param pixelGrid: 2D array of RGB tuples.
    :param factor: Adjustment factor (>0 to warm, <0 to cool).
    :return: Warmth-adjusted pixel grid.
    """
    adjusted_pixel_grid = []
    for row in pixel_grid:
        adjusted_row = []
        for pixel in row:
            r, g, b = pixel
            r = min(max(0, int(r * (1 + warmth_factor))), 255)  # Increase red
            g = min(max(0, int(g * (1 + warmth_factor))), 255)  # Increase green
            b = min(max(0, int(b * (1 - warmth_factor))), 255)  # Decrease blue
            adjusted_row.append((r, g, b))
        adjusted_pixel_grid.append(adjusted_row)
    return adjusted_pixel_grid

# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
