# GPT_Autograder
Reduces college EE lab grading time from hours to a few minutes!

## Getting Started
1. Download this repository using either `git clone` in your terminal or by using the `Download Zip` option from Github.
2. In your terminal, navigate into the `GPT_Autograder` folder.
3. Run `pip install -r requirements.txt` to install the required python packages.
4. To run the program, type `python isim_autograder.py`. The script should start and immediately error. This is because the correct API keys have not been set yet.

## Adding your Canvas API Key
1. Navigate to [https://canvas.olin.edu/](https://canvas.olin.edu/) (or your school's canvas URL.

> [!TIP]
> If using this program at another school, navigate to the `secret_constants.py` file and replace the `canvas.olin.edu` portion of the `CANVAS_API_URL` variable with your school's URL)

3. After logging in, navigate to the `Account` tab in the upper left corner and select `Settings`. Scroll down until you see the `Approved Integrations` tab, and press the `+ New Access Token`.
4. Type `Autograder` in the purpose field, leave the Expiration date field blank, and Press the `Generate Token` button
5. Copy the resulting string of numbers and letters into the `CANVAS_API_TOKEN` variable in the `secret_constants.py` file.

## Adding your Azure API Key
1. This is a bit trickier. First navigate to [https://portal.azure.com/#browse/all](https://portal.azure.com/#browse/all). If you do not have a resource already, create one or ask your IT administrator to create one for you.
2. Click `Resource Management` in the bar on the left side of your screen, then navigate to `Keys and Endpoints`. Copy either of your two keys into the `GPT_API_TOKEN` in the `secret_constants.py` file.
3. Now, navigate to [https://oai.azure.com/portal](https://oai.azure.com/portal), and using the menu on the left of your screen, select `Deployments`. Create a new deployment using the `+ New Deployment` button. You can set the name to whatever you want, but you must use `gpt-4o` as your model type. Set the `Tokens per Minute Rate Limit (thousands)` to be high enough that you won't throttle the autograding program (each student grade expends about 2000 tokens and takes approximately 3 seconds to complete).
4. 
