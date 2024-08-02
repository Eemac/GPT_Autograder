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
5. Copy the resulting string of numbers and letters into the `CANVAS_API_TOKEN` variable in the `secret_constants.py` file, replacing `...` with your key.

## Adding your Azure API Key
1. This is a bit trickier. First, navigate to [https://portal.azure.com/#browse/all](https://portal.azure.com/#browse/all). If you do not have a resource already, create one or ask your IT administrator to create one for you.
2. Click `Resource Management` in the bar on the left side of your screen, then navigate to `Keys and Endpoints`. Copy either of your two keys into the `GPT_API_TOKEN` in the `secret_constants.py` file, again replacing `...`.
3. Now, navigate to [https://oai.azure.com/portal](https://oai.azure.com/portal), and using the menu on the left of your screen, select `Deployments`. Create a new deployment using the `+ New Deployment` button. You can set the name to whatever you want, but you must use `gpt-4o` as your model type. Set the `Tokens per Minute Rate Limit (thousands)` to be high enough that you won't throttle the auto-grading program (each student grade expends about 2000 tokens and takes approximately 3 seconds to complete). A good starting point is 100k tokens.
4. As of 9/2/2024, if you're working with this tool at the Olin College of Engineering, you won't need to change the `GPT_API_URL` field. In the future, or if you belong to a different institution, this should be changed to match your Azure OpenAI Deployment's endpoint URL.

## Further Work
- A GUI interface (desktop/web app) should be created to allow non-technical users to quickly interface with this tool.
- As of 8/30/2024, the tool only accepts PDF submissions. Text, images, and other submission formats are not too difficult to implement and should be added.
- Data visualization could be helpful, allowing instructors to see where classes or students are struggling

## File Breakdown
- `isim_autograder.py` contains code to interact with the Canvas and Azure OpenAI APIs, and also manage student submission files.
- `secret_constants.py` contains information about the Canvas and Azure OpenAI APIs.
- `requirements.txt` contains a list of library dependencies needed to run the auto-grader. 
- the `assignmentData` folder should stay empty and is used to process files.
