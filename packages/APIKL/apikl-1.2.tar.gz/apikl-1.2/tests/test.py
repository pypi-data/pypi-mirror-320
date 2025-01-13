from APIKL import APIKL

files1 = ['java/testDirectory', 'resources/database.json']
files2 = [r'C:\Users\Виталя\Desktop\APIKL\tests\java\testDirectory\database.xml', 'resources']
locator = APIKL(files1, 6)
locator.find_keys()
locator.find_keys(files2)