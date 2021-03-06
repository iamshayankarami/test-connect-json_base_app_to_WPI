from flask import Flask, request, render_template, url_for, redirect, session, flash
import os, time, sqlite3
import urllib.request
from Back_end_main_service import *

imagesOfProducts = os.path.join("UPLOAD_FOLDER", "PRODUCT_IMG")

app = Flask(__name__)
app.secret_key = 'shayan-karami-secret-key-for-flask'
app.config['ProductImages'] = imagesOfProducts

def get_time():
	return time.asctime()[11:19]

def __check_num(Time):
	return Time[0:2]

def check_img_formath(filename):
    return '.' in filename and filename.rsplit('.')[1].lower() in set(['jpg', 'png', 'jpeg'])


def check_user_logage(user_address):
    if get_user_to(user_address)['user_activation'] == 'log-out':
        return redirect(url_for('login'))

def get_user_requests(username):
    if get_user_to(username)["profile_type"] == "sell_both" or get_user_to(username)["profile_type"] == "sell_product":
        return get_user_to(username)["requests_for_user"]
    elif get_user_to(username)["profile_type"] == "sell_both" or get_user_to(username)["profile_type"] == "sell_reserv_time":
        return get_user_to(username)["timeline"]

@app.route('/', methods=['POST', 'GET'])
def main_page():
    if 'username' in session:
        check_user_logage(session["user_address"])
        user_data = get_user_to(session["user_address"])
        all_that_address = get_all_products_location(session["user_address"]["location"])
        #return str(all_that_address["products"][0])
        return render_template('main_show_page.html', products=all_that_address)
    return render_template('welcome.php')

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.route('/profile', methods=["GET", "POST"])
def index():
    if 'username' in session:
        check_user_logage(session["user_address"])
        print(session["username"], session["user_address"])
        user_data = get_user_to(session["user_address"])
        #print(user_data["profile_type"])
        personal_requests = user_data['requests_for_user']
        return render_template("profile.html", username=session["user_address"]["username"], porsonal_requests=personal_requests, profile_type=user_data["profile_type"])

@app.route('/singin', methods=['GET', 'POST'])
def test_in_here():
    if "username" not in session:
        ip_address = request.remote_addr
        if request.method == 'POST':
            return_data = {"name": request.form["name"], "email": request.form["email"], "username": request.form["username"], "password": make_password_to_save(request.form["password"]), "work": request.form["work"], "product_or_time_reservs": request.form['job_product'], "location": request.form["location"], "device_ip_address": ip_address}
            singin_form(return_data)
            #add_user_profile_address(request.form["username"], request.form["location"])
            session["username"] = request.form["username"]
            session["user_address"] = {"username": return_data["username"], "location": return_data["location"]}
            if return_data["product_or_time_reservs"] == "sell_product":
                return redirect(url_for("index"))
            else:
                return redirect(url_for("test_set_time_line"))
        return render_template('singin.html')
    return redirect(url_for("index"))

@app.route('/singin/set_time_line', methods=['POST', 'GET'])
def test_set_time_line():
    if "username" in session:
        check_user_logage(session["user_address"])
        #add ip_address checks
        main_data = get_user_to(session["user_address"])
        if request.method == 'POST':
            if main_data["profile_type"] == "sell_both" or main_data["profile_type"] == "sell_reserv_time":
                input_timeline = request.form["timeline"]
                print(input_timeline)
                if input_timeline == "":
                    timeline = time_line_for_every_day("0/24/60")
                else:
                    timeline = time_line_for_every_day(input_timeline)
                main_data["timeline"] = timeline
                change_profile_D(main_data, session["user_address"])
                return redirect(url_for('customize_timeline'))
        return render_template("customize_selling.html")

@app.route('/custom_main_time_line', methods=['POST', 'GET'])
def customize_timeline():
    if "username" in session:
        check_user_logage(session["user_address"])
        return_data = get_user_to(session["user_address"])
        if return_data["profile_type"] == "sell_both" or return_data["profile_type"] == "sell_reserv_time":
            GTS = get_user_to(session["user_address"])["timeline"]
            if request.method == 'POST':
                main_data = [element for element in request.form]
                return_data["timeline"] = main_data[:len(main_data)-1]
                #return_data["product_or_time_reservs"] = [TimeS for TimeS in main_data if TimeS not in check_time_requests(return_data["requests_for_user"])]
                change_profile_D(return_data, session["user_address"])
                return redirect(url_for("index"))
        return render_template('custom_times.html', re=GTS, re_len=len(GTS))

@app.route('/check_profile_type', methods=['POST', 'GET'])
def check_profile_type():
    if request.method == 'POST':
        if request.form['profile_type'] == "bussines":
            return redirect(url_for("test_in_here", user_profile_type="bussines"))
    return render_template("check_profile_type.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if "username" not in session:
        if request.method == 'POST':
            user_name = request.form["username"]
            password = make_password_to_save(request.form["password"])
            LOGIN_CHECK = Longin(user_name, password)
            if LOGIN_CHECK == "loggin_good":
                session["username"] = user_name
                session["user_address"] = {"username": get_user_information_but_without_has_user_location(user_name)["public"]["username"], "location": get_user_information_but_without_has_user_location(user_name)["public"]["location"]}
                return redirect(url_for("index"))
            else:
                flash(LOGIN_CHECK)
        return render_template("login.html")
    return redirect(url_for("index"))

@app.route('/show_all')
def SHOW_ALL():
    #ip_add = request.remote_addr
    if 'username' in session:
        username=session['username']
        check_user_logage(session["user_address"])
        user_data=get_user_to(session["user_address"])
        show_data = show_all_users_poblic_data_in_user_location(user_data[1]['location'])
        return ''.join([f'''<a href={url_for('show_user', show_username=users[1]['username'])}>{users[1]['username']} </a><b>{users[1]['work']} </b><br><br>''' for users in show_data if users[1]['username'] != username])
    return redirect(url_for('index'))


@app.route('/show_data_of', methods=['POST', 'GET'])
def show_user():
    if 'username' in session:
        show_username = request.args.get('show_username', None)
        username = session['username']
        check_user_logage(session["user_address"])
        status = send_Request(username, show_username)
        timelines = status.check_time_line()
        if request.method == 'POST':
            select = request.form.get('select_form_time')
            status.chose_time_to_send(select)
            status.send_request_to_user_in_command_line()
            return redirect(url_for('show_my_send_requests'))
        return render_template('show_all.html', time_line=timelines)
    return redirect(url_for('index'))

@app.route('/show_my_send_requests', methods=['POST', 'GET'])
def show_my_send_requests():
    if 'username' in session:
        check_user_logage(session["user_address"])
        all_of_my_request = get_user_to(session['username'])[3]['send_requests']
        send_text = []
        for re in all_of_my_request:
            send_text.append([f"{re['request_to']} {re['time']} {re['request_activ']}", make_password_to_save(f"{re['request_to']} {re['time']} {re['request_from']}")])
        return render_template('show_my_sends_requets.html', data=send_text)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    #ip_add = request.remote_addr
    if 'username' in session:
        LogOuT(session['username'])
        session.pop('username', None)
        return redirect(url_for("main_page"))
    return redirect(url_for('main_page'))

@app.route('/add_new_product', methods=['POST', 'GET'])
def add_new_product():
    if "username" in session:
        check_user_logage(session["user_address"])
        user_data = get_user_to(session["user_address"])
        #if user_data["profile_type"] == "sell_both" or user_data["profile_type"] == "sell_product":
        if request.method == 'POST':
            new_product = {"product_seller": session["username"], 'product_name': request.form['product_name'], 'product_cpacity': request.form['product_cpacity'], 'product_price': request.form['product_price'], 'product_activ': 'new_product'}
            new_product["product_address"] = make_password_to_save(new_product["product_seller"] + new_product["product_name"] + new_product["product_cpacity"] + new_product["product_price"])
            print(new_product["product_address"])
            File = request.files['file']
            if File and check_img_formath(File.filename):
                filename = new_product["product_address"] + ".jpeg"
                #File.save(os.path.join("/media/shayan/SHAYAN/SHAYAN2/json_base_app_database/UPLOAD_FOLDER/PRODUCT_IMG", filename))
                new_product["product_image"] = os.path.join("UPLOAD_FOLDER", "PRODUCT_IMG", filename)
            else:
                new_product["product_image"] = os.path.join("/home/shayan/Downloads", "icons8-product-64.png")
            save_new_product(session["user_address"], new_product, new_product["product_address"]) 
            return redirect(url_for("index"))
    return render_template('add_new_product.html')

@app.route("/time_buy/<username>", methods=["POST", "GET"])
def show_products_or_timelines(username):
    if "username" in session:
        check_user_logage(session["user_address"])
        get_require_username_data = get_user_information_but_without_has_user_location(username)
        user_timelines = [time for time in get_require_username_data["timeline"]]
        if request.method == "POST":
            input_time = request.form["input_time"]
            check = send_time_request(username, input_time, session["user_address"])
            print(check)
            if check["ERROR"] == "time_is_not_valibel":
                flash(check["ERROR"])
            else:
                redirect(url_for("index"))
        return render_template("show_profile.html", user_info=get_require_username_data["public"], timelines=user_timelines)
    return redirect(url_for("login"))

@app.route('/product/<product_address>', methods=['POST', 'GET'])
def show_product(product_address):
    return str(find_product(product_address))

@app.route("/show_all_products")
def show_user_requests_and_change_it_by_user():
    if "username" in session:
        check_user_logage(session["user_address"])
        user_products = get_user_to(session["user_address"])["products"]
        #products_images = "/media/shayan/SHAYAN/SHAYAN 2/json_base_app_database/UPLOAD_FOLDER/PRODUCT_IMG/0ab5714cc863b181ecee2f7dd64824c36aac22afd46dab1869325464c1be177e.jpeg"
        return render_template("show_and_edit_products.html", products=user_products)#, product_images=products_images)
@app.route("/show_all_products/<username>")
def show_user_products(username):
    #set timelines and ranges to show products
    if "username" in session:
        check_user_logage(session["user_address"])
        if username == session["username"]:
            return redirect(url_for("show_user_requests_and_change_it_by_user"))
        else:
            user_products = get_user_to(session["user_address"])["products"]
        return render_template("show_and_edit_products.html", products=user_products)

if __name__ == '__main__':
	app.run("0.0.0.0", port=4000, debug=True)