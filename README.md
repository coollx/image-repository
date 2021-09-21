# image-repository
This is a light weight CLI image repository, it allows you to upload, delete, search, display images fome command line. It can automatically add tags to your image using a pretrained deep learning algorithm.


Dependencies:
    opencv-python  
    numpy
    pandas
    sqlite
    tensorflow 2.6.0
    tensorflow-hub 

Platform: windows 10

Installation:
1.install all the denpendencies
2.make sure the folder has the following structure:
repository.py
image_detector.py
labels.csv
pretrained
    |-saved_model.pb
    |-variables
        |-variables.data-00000-of-00001
        |-variables.index
README.txt
test images



usage:
1. To run the program, enter `python repository.py` in terminal
2. to upload images, using `upload` command and follow the instructions. In brief, the user will need to privide the right path to image and an image name.
3. `show all` command to display the information of all uploaded images: image ID, image name, image tags, upload time.
4. `display` command allows you to display a specific image in database, in case of duplicate image name, please follow the instructions.
5. `delete` command allows you to delete a specific image.
6. `analyze` command automatically add tags to images in database, attention, the first run of this time will take some time, please be patient.
7. `search` command allowd you to search images with a specified category
8. `quit` command to hault the program.

