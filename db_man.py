from CommonCode import AuthTools, DbTools

db = DbTools()


def process_week(week=None):
    if week is not None:
        if not isinstance(week, int):
            week = None

    return db.read("SELECT max(sl_week_num) FROM tb_slots", f_all=False)[0] if week is None else week


def get_scores_data(week, do_order=True):
    q_scores = """
SELECT tt.tm_name, sl_day_1, sl_day_2, sl_day_3, sl_day_4, sl_day_5, sl_day_6, sl_kills, sl_total
FROM tb_slots
LEFT JOIN tb_team tt ON tt.tm_pk_id = tb_slots.sl_fk_tm_pk_id
WHERE sl_week_num = ? """
    if do_order:
        q_scores += """ORDER BY sl_total DESC, sl_kills DESC, 
sl_day_6 DESC, sl_day_5 DESC, sl_day_4 DESC, sl_day_3 DESC, sl_day_2 DESC, sl_day_1 DESC"""

    week = process_week(week)
    return {week: {"scores": db.read(q_scores, (week,))}}


def get_slots_data(week):
    q_slots = """
SELECT sl_slot_num, tt.tm_name, tt.tm_dp_path, tt.tm_pk_id
FROM tb_slots
LEFT JOIN tb_team tt ON tt.tm_pk_id = tb_slots.sl_fk_tm_pk_id
WHERE sl_week_num = ?
ORDER BY sl_slot_num"""

    week = process_week(week)
    return {week: {"slots": db.read(q_slots, (week,))}}


class Manage:
    @classmethod
    def load_dash(cls, week):
        week = process_week(week)
        return {
            "sel_week": week,
            "max_week": process_week(),
            "slots": get_slots_data(week)[week]["slots"],
            "scores": get_scores_data(week, do_order=False)[week]["scores"],
            "teams": [[str(team[0]), team[1]] for team in cls.get_teams()]
        }

    @staticmethod
    def get_teams(ind=None):
        q = """
        SELECT tm_pk_id, tm_name, tm_dp_path
        FROM tb_team
        ORDER BY tm_name"""
        q_sel = " WHERE tm_pk_id = ?"

        if ind is not None:
            q += q_sel

        return db.read(q, (ind,) if ind else ())

    @staticmethod
    def task_endpoint(task, data):
        if task == "modify_slots":
            q_slot_add = '''INSERT INTO tb_slots (sl_week_num, sl_slot_num, sl_fk_tm_pk_id) VALUES (?,?,?)'''
            q_slot_delete = '''DELETE FROM tb_slots WHERE sl_week_num = ? AND sl_slot_num = ? AND sl_fk_tm_pk_id = ?'''
            action = data.get("action")
            if action == "delete":
                query = q_slot_delete
            elif action == "add":
                query = q_slot_add
            else:
                return "Error: unknown action requested"

            print("task: " + action)
            print("data: " + str(data.get('data')))
            db.write(query, (
                data.get("data").get("week"),
                data.get("data").get("slot"),
                data.get("data").get("team_id")
            ))

        elif task == "update_scores":
            q_get_team_ids = '''SELECT sl_fk_tm_pk_id FROM tb_slots WHERE sl_week_num = ?'''
            q_update_scores_pt1 = '''UPDATE tb_slots SET'''
            q_update_scores_pt2 = ''' WHERE sl_fk_tm_pk_id = ? AND sl_week_num = ?'''

            t_id_set = db.read(q_get_team_ids, (data['week'],))
            t_id_set = [tup + (data['week'],) for tup in t_id_set]

            for key in data.keys():
                print(key + ": " + str(data[key]))
                if key == "week":
                    print("skipping...")
                    break

                # list comprehension
                t_id_set = [tup[:-2] + (data[key][i],) + tup[-2:] for i, tup in enumerate(t_id_set)]

                if key == "day1":
                    q_update_scores_pt1 += " sl_day_1 = ?,"
                elif key == "day2":
                    q_update_scores_pt1 += " sl_day_2 = ?,"
                elif key == "day3":
                    q_update_scores_pt1 += " sl_day_3 = ?,"
                elif key == "day4":
                    q_update_scores_pt1 += " sl_day_4 = ?,"
                elif key == "day5":
                    q_update_scores_pt1 += " sl_day_5 = ?,"
                elif key == "day6":
                    q_update_scores_pt1 += " sl_day_6 = ?,"
                elif key == "kills":
                    q_update_scores_pt1 += " sl_kills = ?,"
                elif key == "total":
                    q_update_scores_pt1 += " sl_total = ?,"
            q_update_scores_pt1 = q_update_scores_pt1[:-1] + q_update_scores_pt2

            print(t_id_set)
            print(q_update_scores_pt1)

            db.lock.acquire(True)
            db.cur.executemany(q_update_scores_pt1, t_id_set)
            db.db.commit()
            db.lock.release()

        elif task == "add_week":
            pass

        return "OK"


class Auth:
    @staticmethod
    def do_login(username, password):
        q_fetch_hash = '''SELECT lg_pw_hash, lg_pk_id FROM tb_login WHERE lg_username = ?'''
        q_put_token = '''UPDATE tb_login SET lg_token = ? WHERE lg_pk_id = ?'''
        res = db.read(q_fetch_hash, (username,), f_all=False)
        if res is None:
            return None         # no such username

        pw_hash, user_num = res
        print("h: {}, n: {}".format(pw_hash, user_num))
        if AuthTools.password_hash_verify(password, pw_hash):
            token = AuthTools.make_token()
            print("token: " + token)
            db.write(q_put_token, (token, user_num))
            return token, user_num

        return False            # for wrong password

    @staticmethod
    def check_token(user_num, token):
        q_check_token = '''SELECT COUNT(*) FROM tb_login WHERE lg_pk_id = ? AND lg_token = ?'''
        return db.read(q_check_token, (user_num, token), f_all=False)[0] == 1
