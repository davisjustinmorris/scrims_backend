$(document).ready(function () {
    // #edit_slot & #add_week close
    $(`#edit_slot, #edit_slot > button, #add_week, #add_week > button`)
        .on('click', () => { $(`#edit_slot`).removeClass("shown"); $(`#add_week`).removeClass("shown") })
        .children().on('click', function () {return false;});

    // slots .list click listener
    $(`#slot > div > .list`).on('click', function () {
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

    // button[add_slot] click listener
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

     // button[add_week] click listener
    $('nav button[name="add_week"]').on('click', function () {
        $(`#add_week .body`).append(populate_team_list());
        console.log(populate_team_list());
        $('aside#add_week').addClass('shown');
    });

    $('#add_week button[name="add"]').on('click', function () {
        let sel = populate_team_list(null);
        console.log("new add slot invoked; sel: ", sel);
        $('#add_week .body').append(populate_team_list());
    });
});