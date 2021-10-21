function validateForm() {
    var habit_name = document.forms["input_new_habit"]["habit_name"].value;
    var start_date = document.forms["input_new_habit"]["start_date"].value;
    var goal_streaks = document.forms["input_new_habit"]["goal_streaks"].value;
    if (habit_name == "") {
      alert("Input new habit name");
      return false;
    }
  }