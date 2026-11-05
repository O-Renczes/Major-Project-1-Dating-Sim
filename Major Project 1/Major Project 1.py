import json
import os
import flet as ft
import shutil


#Opens the json file and returns everything in it
def load_data():
    with open('data.json', 'r') as infile:
        return json.load(infile)


#Takes a dictionary and the key, returns True if an info list is found
def has_info_list(d, key):
    val = d.get(key, [])
    return any(isinstance(item, list) for item in val)


#Takes in the new content for the save file, overwrites the file accordingly. Will create directories and files accordingly to properly store the information
def save_data(info):
    try:
        os.makedirs("Profile Photos", exist_ok=True)
    except OSError:
        pass

    if os.path.getsize('data.json') == 0:
        with open('data.json', 'w') as outfile:
            json.dump({}, outfile)

    current = load_data()
    with open('data.json', 'w') as outfile:
        current = current | info
        json.dump(current, outfile)


#Takes in an integer, returns the question and the type of question to be formatted later
def access_question(num: int) -> list:
    question_dict = {1: ["What is your first name?", 1],
                     2: ["What is your last name?", 1],
                     3: ["What is your age?", 1],
                     4: ["What is your gender?", "Male", "Female"],
                     5: ["Do you enjoy cooking?", "Yes", "No", 2],
                     6: ["How often do you cook?", "Daily", "Most Days", "Twice Weekly", "Bimonthly", "Monthly or less", 3],
                     7: ["Do you enjoy playing games?", "Yes", "No", 2],
                     8 : ["What type of game do you most often play?", "Card Games", "Tabletop Games", "Video Games", "Role-Playing Games", "Strategy Games", 3],
                     9: ["Do you enjoy reading?", "Yes", "No", 2],
                     10: ["What genre do you most often read?", "Thrillers", "Mysteries", "Fantasy",  "Science Fiction", "Romance", 3],
                     11: ["Do you enjoy listening to music?", "Yes", "No", 2],
                     12: ["What genre do you most listen to?", "Pop", "Rock", "Country",  "Electronic",  "Instrumental", 3],
                     13: ["Do you enjoy playing sports?", "Yes", "No",2],
                     14: ["What type of sport do you most often play?", "Solo, competitive", "Solo, recreational", "Team, competitive", "Team, recreational", "None of the above", 3],
                     15: ["Do you enjoy crafting or fashioning objects?", "Yes", "No", 2],
                     16: ["What type of activity do you most enjoy?",  "Sewing" , "Woodworking",  "Gardening",  "Drawing, painting & illustrating", "Other", 3],
                     17: ["Would you describe yourself as:", "Orderly", "Messy", 2],
                     18: ["Would you describe yourself as:", "Extroverted", "Introverted", 2],
                     19: ["Would you describe yourself as:", "Curious", "Consistent", 2],
                     20: ["Would you describe yourself as:", "Outdoorsy", "Indoorsy", 2],
                     21: ["Would you describe yourself as:", "High-Energy", "Low-Energy", 2]}
    return  question_dict[num]


#Given a user's and a partner's information, calculates the delta between them (severely reduced if age delta is too high) and return that score
def score_similarity(user, partner):
    score = 0
    if (user[2]/2)+7 <= partner[2]:
        pass
    else:
        score += 100
    for trait in range(4, 20):
        score += abs(user[trait]-partner[trait])
    return score


#Takes in the current username, returns the best 4 matches for that user
def match_users(username):
    all_data = load_data()
    if username not in all_data:
        return []
    user = all_data[username][1]
    match_dict = {}
    for partner_id, partner_data in all_data.items():
        # Will only compare user to partner if they have enough information in their profile (must have an info list present)
        if len(partner_data) < 2 or not any(isinstance(item, list) for item in partner_data):
            continue
        partner_info = partner_data[1]
        #If the user is the partner, goes to the next potential partner
        if user[0] + user[1] == partner_info[0] + partner_info[1]:
            continue
        #Formats name properly
        full_name = f"{partner_info[0]} {partner_info[1]}"
        #If user genders are not the same, scores their compatibility
        if user[3] != partner_info[3]:
            match_dict[full_name] = score_similarity(user, partner_info)

    sorted_match = sorted(match_dict, key=lambda k: match_dict[k], reverse=True)
    return sorted_match[0:4]


def main_page(page : ft.Page):
    file_picker = ft.FilePicker()


    #Displays the page upon starting the program, including login and register options
    def entry_page():
        page.controls.clear()
        page.floating_action_button = None
        page.bgcolor = ft.Colors.BLUE_GREY_100
        login_button = ft.Container(
            alignment = ft.Alignment.CENTER,
            content = ft.Button(
            content = "Login",
            on_click = login_page,
            width = 125,
            height= 75,
            expand=True,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: ft.Colors.WHITE_12,
                    ft.ControlState.DEFAULT: ft.Colors.WHITE}
        )))
        register_button = ft.Container(
            alignment = ft.Alignment.CENTER,
            content = ft.Button(
            content = "Register",
            on_click = registration_page,
            expand = True,
            width = 125,
            height= 75,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: ft.Colors.WHITE_12,
                    ft.ControlState.DEFAULT: ft.Colors.WHITE}
        )))
        name = ft.Container(
            alignment = ft.Alignment.CENTER,
            expand = True,
            bgcolor = ft.Colors.BLACK,
            content = ft.Text("Amāre", size= 48, weight= ft.FontWeight.W_600, color = ft.Colors.WHITE)
        )
        page.add(ft.Container(
            content = ft.Column([name, login_button, register_button])))


    #When uploading image files for your profile photo, routes the image to the correct folder and stores the path to the folder in the users save data
    async def handle_pick_files(username):
        a = await file_picker.pick_files(allow_multiple=False, file_type= ft.FilePickerFileType.CUSTOM, allowed_extensions= [".jpg", ".png", ".jpeg"])
        file = a[0]
        if file:
            destination_path = os.path.join("Profile Photos", file.name)
            user_data = load_data()
            if username in user_data:
                new_data = user_data[username]
                if len(load_data()[username])<=2:
                    new_data.append(file.name)
                    save_data({username : new_data})
                else:
                    new_data[-1] = file.name
                    save_data({username : new_data})
            try:
                if file.path:
                    shutil.copy(file.path, destination_path)
            except:
                pass


    #Buttons for user to upload a profile photo, enter user information and find matches. Inputs are restricted to aovid finding matches without adequate user information
    def user_page(username, password):
        page.bgcolor = ft.Colors.BLUE_GREY_100
        page.controls.clear()
        page.floating_action_button = None
        page.floating_action_button = ft.FloatingActionButton("Quit", on_click = lambda : entry_page())
        match_button = ft.Button(
            content= 'Find Matches',
            #on click is modified to prevent users matching without having filled in their profiles
            on_click = lambda : match_page(username, password) if has_info_list(load_data(), username) else None,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: ft.Colors.WHITE_12,
                    ft.ControlState.DEFAULT: ft.Colors.WHITE}
        ))
        info_button = ft.Button(
            content= "Update Profile",
            on_click = lambda : display_questions(username, password),
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: ft.Colors.WHITE_12,
                    ft.ControlState.DEFAULT: ft.Colors.WHITE}
        ))
        upload = ft.Button(
            content="Upload Profile Photo",
            on_click= lambda : page.run_task(handle_pick_files, username),
            style = ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: ft.Colors.WHITE_12,
                    ft.ControlState.DEFAULT: ft.Colors.WHITE}
        ))
        page.add(match_button, info_button, upload)


    #Prints all questions and record inputs
    def display_questions(username, password):
        page.bgcolor = ft.Colors.BLACK
        question_answers = []
        page.controls.clear()
        page.floating_action_button = None
        #Formats user answers into a cleaner format of first name and last name, followed by integer value of answers
        def extract_answers():
            answers = [question_answers[0][0].value, question_answers[1][0].value]
            for x in question_answers:
                for y in x:
                    try:
                        answers.append(int(y.value))
                    except ValueError:
                        pass
            return answers
        def submit_click():
            answers= extract_answers()
            if len(load_data()[username]) >= 2:
                save_data({username: [password, answers, load_data()[username][-1]]})
            else:
                save_data({username: [password, answers]})
            user_page(username, password)
        #Formats each question into a list to be displayed
        for question in range(1,21):
            question_number = access_question(question)
            if question_number[-1] == 3:
                question_answers.append([ft.Text(f"{question_number[0]}"),
                    ft.RadioGroup(
                    content= ft.Column(controls = [
                        ft.Radio(value= "1", label = question_number[1]),
                        ft.Radio(value= "2", label= question_number[2]),
                        ft.Radio(value= "3", label= question_number[3]),
                        ft.Radio(value= "4" , label= question_number[4]),
                        ft.Radio(value= "5", label= question_number[5])
                    ]))])
            elif question_number[-1] == 1:
                question_answers.append([ft.TextField(label= question_number[0], hint_text= question_number[0])])
            else:
                question_answers.append([ft.Text(f"{question_number[0]}"),
                    ft.RadioGroup(
                    content=ft.Column(controls = [
                        ft.Radio(value="1", label= question_number[1]),
                        ft.Radio(value="5", label= question_number[2]),
                    ]))])

        page.floating_action_button = ft.FloatingActionButton("Submit", on_click = lambda : submit_click() if all(extract_answers()) else None)

        page.add(ft.Row(
            expand= True,
            controls =
            [ft.Container(expand= True, bgcolor = ft.Colors.BLUE_GREY_100),
            ft.Container(
            expand = True,
            content= ft.Column(
                controls= [*question for question in question_answers], expand = True, scroll = ft.ScrollMode.ALWAYS),
        )]))


    #Formats the current user's matches into partners avatars and names
    def match_page(username, password):
        page.bgcolor = ft.Colors.BLUE_GREY_100
        page.controls.clear()
        page.floating_action_button = None
        page.floating_action_button = ft.FloatingActionButton("Back", on_click = lambda : user_page(username, password))
        matches = match_users(username)
        #Finds an image file attached to a user profile, if no image, returns none
        def find_src(match):
            data = load_data()
            entry = next((v for v in data.values() if len(v) > 1 and f"{v[1][0]} {v[1][1]}" == match), None)
            return entry[2] if entry is not None and len(entry) > 2 else None

        page.add(ft.GridView(
            runs_count = 2,
            spacing = 8,
            expand = True,
            child_aspect_ratio = 1.0,
            controls= [
                ft.Container(expand= True, bgcolor = ft.Colors.BLACK, content=
                ft.Column(controls = [ft.Text(str(match), size = 24, text_align = ft.TextAlign.CENTER),
                                      #image source gets the saved path to the file given the partners first and last name
                                      ft.CircleAvatar(foreground_image_src= find_src(match),
                                                      radius = 100,
                                                      expand=True)]), alignment = ft.Alignment.CENTER)
                for match in matches
            ]
        ))


    #Allows a user to input their username and password
    def login_page():
        page.bgcolor = ft.Colors.BLUE_GREY_100
        page.controls.clear()
        page.floating_action_button = None
        def submit(e):
            collected_username = username.value
            collected_password =  password.value
            if collected_username in load_data() and collected_password == load_data()[collected_username][0]:
                user_page(collected_username, collected_password)
            else:
                error_text.value = "Incorrect Username or Password"
                page.update()

        username = ft.TextField(label=  "Username", hint_text= "Please enter your username", cursor_color = ft.Colors.BLACK, color= ft.Colors.BLACK, bgcolor = ft.Colors.WHITE)
        password = ft.TextField(label= "Password", hint_text= "Please enter your password", password= True, cursor_color = ft.Colors.BLACK, color= ft.Colors.BLACK, bgcolor = ft.Colors.WHITE)
        error_text = ft.Text("", color = ft.Colors.BLACK)
        page.floating_action_button = ft.FloatingActionButton("Login", on_click = submit)
        page.add(ft.Container(
            expand = True,
            content= ft.Column([username, password, error_text],),
            align = ft.Alignment.CENTER
        ))


    #Allows a user to create an account
    def registration_page():
        page.bgcolor = ft.Colors.BLUE_GREY_100
        page.controls.clear()
        page.floating_action_button = None
        def submit(e):
            collected_username = username.value
            collected_password = password.value
            collected_con_password = confirm_password.value
            if collected_password == collected_con_password:
                save_data({collected_username: [collected_con_password]})
                user_page(collected_username, collected_password)
            else:
                error_text.value = "Your passwords do not match"
                page.update()
        username= ft.TextField(label= "Username", hint_text= "Please enter your username", cursor_color = ft.Colors.BLACK, color= ft.Colors.BLACK, bgcolor = ft.Colors.WHITE)
        password = ft.TextField(label= "Password", hint_text= "Please enter your password", password = True, cursor_color = ft.Colors.BLACK, color= ft.Colors.BLACK, bgcolor = ft.Colors.WHITE)
        error_text = ft.Text("", color=ft.Colors.BLACK)
        confirm_password = ft.TextField(label= "Confirm Password", hint_text= "Confirm Password", password= True, cursor_color = ft.Colors.BLACK, color= ft.Colors.BLACK, bgcolor = ft.Colors.WHITE)
        page.floating_action_button = ft.FloatingActionButton("Register", on_click = submit, width= 100)
        page.add(ft.Container(
            expand = True,
            content= ft.Column([username, password, confirm_password, error_text]),
            align = ft.Alignment.CENTER
        ))


    entry_page()


#Runs the program, selects the correct directory
def main():
    ft.run(main_page, assets_dir= "Profile Photos")


if __name__ == "__main__":
    main()


