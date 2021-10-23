from logging import NullHandler
from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from flaskext.mysql import MySQL
from datetime import date, datetime

app = Flask(__name__, static_folder="static", template_folder="template")

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'habitsdb'
app.config['MYSQL_DATABASE_Host'] = 'localhost'
mysql.init_app(app)

#main screen
@app.route("/main")
def main():
  conn = mysql.connect()
  cursor =conn.cursor()
  cursor.execute("SELECT * from habit_info")
  db_habits = cursor.fetchall()
  habits = []
  color = ""
  status = ""
  check = 0
  for row in db_habits:
    cursor.execute("SELECT checked FROM habit_check WHERE habit_id = %s AND check_date = %s",(row[0],date.today()))
    db_habit_check = cursor.fetchone()

    if cursor.rowcount == 0:
      cursor.execute("INSERT INTO habit_check (habit_id) values (%s)", (row[0],))
      conn.commit()
    else:
      check = db_habit_check[0]

    if check == 0:
      color = "E5E7E9"
      status = "Check"
    else:
      color = "58D68D"
      status = "Checked"

    habits.append({"habit_id": row[0],"habit_name": row[1],"goal_streaks": row[3], "real_streaks" : row[4], "checked" : check, "color": color, "status": status})

  return render_template('index.html', habits=habits)

#check habit redirect
@app.route("/checkHabit", methods=["POST"])
def checkHabit():
  checked = int(request.form["checked"])
  habit_id = int(request.form["habit_id"])
  color = ""
  status = ""
  conn = mysql.connect()
  cursor = conn.cursor()
  if checked == 0:
    checked = 1
    color = "58D68D"
    status = "Checked"
    cursor.execute("UPDATE habit_check SET checked = %s WHERE habit_id = %s AND check_date = %s", (checked, habit_id,date.today(),))
    cursor.execute("UPDATE habit_info SET real_streaks = real_streaks + 1 WHERE habit_id = %s", (habit_id,))
  elif checked == 1:
    checked = 0
    color = "E5E7E9"
    status = "Check"
    cursor.execute("UPDATE habit_check SET checked = %s WHERE habit_id = %s AND check_date = %s", (checked, habit_id,date.today(),))
    cursor.execute("UPDATE habit_info SET real_streaks = real_streaks - 1 WHERE habit_id = %s", (habit_id,))
  
  conn.commit()
  conn.close()
  
  return redirect(url_for("main", color=color, status=status))

#add new habit screen 
@app.route("/newHabit")
def newHabit():
  return render_template('new_habit.html')

#add new habit redirect
@app.route("/register", methods=["POST"])
def register():
  habit_name = request.form["habit_name"]
  start_date = datetime.strptime(request.form["start_date"],"%Y-%m-%d")
  goal_streaks = int(request.form["goal_streaks"])

  conn = mysql.connect()
  cursor =conn.cursor()
  cursor.execute("INSERT INTO habit_info (habit_name, start_date, goal_streaks, real_streaks) values (% s, % s, % s, % s)", 
                  (habit_name,start_date,goal_streaks,0,))
  conn.commit()
  conn.close()

  return redirect(url_for("main"))

# habit detail screen
@app.route("/habitDetail",methods=["POST"])
def habitDetail():
  habit_id = int(request.form["habit_detail"])

  conn = mysql.connect()
  cursor =conn.cursor()
  cursor.execute("SELECT * FROM habit_info WHERE habit_id = %s", (habit_id,))
  row = cursor.fetchone()
  habit_detail = []

  habit_detail.append({"habit_name": row[1],"start_date": row[2], "goal_streaks": row[3], "real_streaks" : row[4]})

  print(habit_detail)

  return render_template("habit_detail.html", habit_detail=habit_detail[0])

# delete habit redirect
@app.route("/deleteHabit", methods=["POST"])
def deleteHabit():
  habit_id = int(request.form["habit_delete"])
  print(habit_id)
  conn = mysql.connect()
  cursor =conn.cursor()
  cursor.execute("DELETE FROM habit_info WHERE habit_id = %s",(habit_id,))
  conn.commit()
  conn.close()
  print("Delete success")
  return redirect(url_for("main"))

if __name__ == "__main__":
  app.run()