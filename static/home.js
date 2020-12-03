$(document).ready(function () {
// GENERAL & COMMON
    // generalised ajax push >>> >>> >>>
    function ajax_push(url, data) {
        $.ajax(
            url,
            {
                type: "POST",
                contentType: "application/json;  charset=utf-8;",
                data: JSON.stringify(data),
                success: function () { location.reload(); },
                error: function () { alert("something went wrong communicating!"); }
            }
        );
    }

    // check str is int
    function check_str_int(val, check_empty_str = true) {
        if (!isNaN(val) && val !== "")
            if (val === String(parseInt(val)))
                return true;

        return false;
    }

    // creates row with sel-option
    function populate_team_list() {
        let tg =
        `<div class="list">
            <input type="text" name="slot" size="2" placeholder="Slot #">
            <select>
                <option selected hidden disabled>--Choose--</option>`;

        teams.forEach(details => tg += `<option value="${details[0]}">${details[1]}</option>\n`);
        tg +=`
            </select>
        </div>`;
        return tg;
    }

    // #edit_slot & #add_week close
    $(`#edit_slot, #edit_slot > button, #add_week, #add_week > button`)
        .on('click', () => { $(`#edit_slot`).removeClass("shown"); $(`#add_week`).removeClass("shown") })
        .children().on('click', function () {return false;});


// SLOT LIST
    // #slot .list click listener
    $(`#slot> div > .list`).on('click', function () {
        $('aside#edit_slot .container img').remove();
        $('aside#edit_slot .container').append($(this).find('img').clone());
        $('aside#edit_slot .container input').val($(this).find('span:first-child').html());
        $("#edit_slot .container button:last-child").hide();
        $("#edit_slot .container button:not(:last-child)").show();

        let sel = $('aside#edit_slot .container select');
        let team_id = this.id;
        sel.empty();
        teams.forEach(function (details) {
            if (team_id === details[0])
                sel.append(`<option value="${details[0]}" selected>${details[1]}</option>`);
            else
                sel.append(`<option value="${details[0]}">${details[1]}</option>`);
        });

        $('aside#edit_slot').addClass('shown');
    });

    // #slot button[add_slot] click listener
    $(`#slot summary button`).on('click', function () {
        let sel = $('#edit_slot .container select');
        sel.empty();
        sel.append(`<option selected hidden disabled>--Choose--</option>`);
        teams.forEach(details => sel.append(`<option value="${details[0]}">${details[1]}</option>`));

        $('#edit_slot .container img').remove();
        $('#edit_slot .container input').val("");
        $('#edit_slot .container button:last-child').show();
        $('#edit_slot .container button:not(:last-child)').hide();
        $('#edit_slot').addClass('shown');
});


// UPDATE SCORES
    // button[update_scores] listener >>>
    $(`#score summary button[name="update_scores"]`).on('click', function () {
        // get selected checkboxes
        let tg_lis = [];
        $(`input[name="select_update"]:checked`).each((a, b) => tg_lis.push(b.value));

        // if none sel; alert
        if (tg_lis.length === 0) { alert("no columns selected for update"); return ; }

        // convert target column:nth-child inp-value to list
        let upload_dict = {}, flag_invalid_spotted = false, upload_cols, key;
        tg_lis.forEach(function (val) {
            // prep list
            upload_cols = [];
            $(`#score table tr:not(:first-child, :last-child) td:nth-child(${parseInt(val) + 1}) input`).each(function (i, score) {
                if (check_str_int(score.value))
                    upload_cols.push(score.value);
                else {
                    upload_cols.push(null);
                    if (score.value !== "") flag_invalid_spotted = true;
                }
            });

            // make dict
            switch (val){
                case "1": key = "day1"; break;
                case "2": key = "day2"; break;
                case "3": key = "day3"; break;
                case "4": key = "day4"; break;
                case "5": key = "day5"; break;
                case "6": key = "day6"; break;
                case "7": key = "kills"; break;
                case "8": key = "total";
            }
            upload_dict[key] = upload_cols;
        });

        // data validation promp
        if (flag_invalid_spotted)
            if (!confirm("Invalid entries spotted! Do you wish to continue? Invalid details will be set empty."))
                return ;

        // ajax push & if success; reload! | else; alert!
        ajax_push("/ajax/update_scores", upload_dict);
    });


// EDIT SLOT
    // add | update | delete
    $(`#edit_slot .container button`).on('click', function () {
        let slot = $(`#edit_slot input`).val();
        let team_id = $(`#edit_slot select`).val();
        if (!check_str_int(slot) || team_id === null){
            alert("Invalid details!");
            return ;
        }
        ajax_push("/ajax/modify_slots", {
            action: this.name,
            data: {
                week: $(`nav ul a.selected`).text(),
                slot: slot,
                team_id: team_id
            }
        });
    });


// ADD WEEK WITH SLOTS
     // nav button[add_week] click listener
    $('nav button[name="add_week"]').on('click', function () {
        $(`#add_week .body`).append(populate_team_list());
        console.log(populate_team_list());
        $('aside#add_week').addClass('shown');
    });

    // #add_week button[add_slot] click listener
    $('#add_week .container button[name="add"]').on('click', function () {
        let sel = populate_team_list(null);
        console.log("new add slot invoked; sel: ", sel);
        $('#add_week .body').append(populate_team_list());
    });

    // submit >>>
    $(`#add_week .container button[name="submit"]`).on('click', function () {
        let slot, team_id, slot_list = [], flag_invalid_spotted = false, week_num;
        $(`#add_week .body .list`).each(function (ii, list) {
            slot = $(list).find("input").val();
            team_id = $(list).find("select").val();
            // data check and push
            if (!check_str_int(slot) || team_id === null){
                console.log("invalid entry list", $(list).find("input"), $(list).find("select"));
                flag_invalid_spotted = true;
            } else {
                slot_list.push([slot, team_id]);
            }
        });
        week_num = $(`#add_week .header input`).val();

        // data validation
        if (slot_list.length === 0) {
            alert("No valid details entered, try again after entering proper data");
            return ;
        }
        if (!check_str_int(week_num)) {
            alert("Enter valid week number!");
            return ;
        }
        if (flag_invalid_spotted)
            if (!confirm("Empty entries spotted! Do you wish to continue? Invalid details will be ignored."))
                return ;

        // send data
        ajax_push("/ajax/add_week", {
            format: ["slot_num", "team_id"],
            data: { slot_team_list: slot_list }
        });
    })
});