<div align="center">

# Smashorpass.ai

<img src="https://github.com/ramsy0dev/smashorpass.ai-scrapper/blob/main/assets/smashorpass.ai.png?raw=true" width=400 />

</div>

---

>__NOTE__: This may not still work if the V2 of smashorpass.ai came out

# What is smashorpass.ai?

A voting based site that lets users vote with 'smash' or 'pass' a given women image that is AI generated. (that's it)

# Reverse engineering smashorpass.ai

The website uses a fairly basic login system when it comes to handling these images. When you first visit it, a request is sent to `https://www.smashorpass.ai/api/images` with the parameters being `{"seenImages": []}`. This parameter contains the field 'seenImages,' which will have a list of image IDs that you have already seen while voting on the site. This field allows us to view all the other images because if you pass the field as empty (with an empty list of image IDs), the server will respond with a random image ID and name, like this: `{"imageUrl":"00039-399213468.png","imageId":34}`. We can then keep track of the given ID each time we send the request and use the imageUrl to download the actual image.

Smashorpass.ai uses Google's cloud storage. If we investigate where the website sends this imageUrl to in order to get the image, we will find that it's sent to `https://storage.googleapis.com/smash-test-images/images/{imageUrl}`. Then, it responds with the image content without any verification or additional steps. The script [smashorpass.py](https://github.com/ramsy0dev/smashorpass.ai-scrapper/blob/main/smashorpass.py) automates all of this for you.

# Prerequisites

You need to install some python packages:

``` bash
pip install requirements.txt
```

# Exploiting

First you will need to get a Cookie, you can get it by visiting the website and opening the developer tab and going to the network tab and reload the page then look at the headers of the second request where you will find the `Cookie` you need to copy it's value and past it the script in the `Cookie` constant at line `40`.

After that, you can just run the script as follows with no special flags or anything, if you stoped it or there was a network issue the script won't download the images that you previously installed

```bash
python smashorpass.py
```

<!-- # Pre-installed images archive

The repo already contains all the images that i could have possible obtained they are archived and located [here]() -->

# License

GPL-v3.0 license
