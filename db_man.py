import sqlite3
from multiprocessing import Lock


DB_Name = 'db.sqlite'
db = sqlite3.connect(DB_Name, check_same_thread=False)
cur = db.cursor()
lock = Lock()


def _db_write(q, val, do_commit=True):
    lock.acquire(True)
    last_row_id = cur.execute(q, val).lastrowid
    if do_commit:
        db.commit()
    lock.release()
    return last_row_id


def _db_read(q, val=(), f_all=True):
    lock.acquire(True)
    if f_all:
        res = cur.execute(q).fetchall() if val == () else cur.execute(q, val).fetchall()
    else:
        res = cur.execute(q).fetchone() if val == () else cur.execute(q, val).fetchone()
    lock.release()
    return res


def process_week(week=None):
    if week is not None:
        if not isinstance(week, int):
            week = None

    return _db_read("SELECT max(sl_week_num) FROM tb_slots", f_all=False)[0] if week is None else week


def get_scores_data(week):
    q_scores = """
SELECT tt.tm_name, sl_day_1, sl_day_2, sl_day_3, sl_day_4, sl_day_5, sl_day_6, sl_kills, sl_total
FROM tb_slots
LEFT JOIN tb_team tt ON tt.tm_pk_id = tb_slots.sl_fk_tm_pk_id
WHERE sl_week_num = ?
ORDER BY sl_total DESC, sl_kills DESC, 
sl_day_6 DESC, sl_day_5 DESC, sl_day_4 DESC, sl_day_3 DESC, sl_day_2 DESC, sl_day_1 DESC"""

    week = process_week(week)
    return {week: {"scores": _db_read(q_scores, (week,))}}


def get_slots_data(week):
    q_slots = """
SELECT sl_slot_num, tt.tm_name, tt.tm_dp_path, tt.tm_pk_id
FROM tb_slots
LEFT JOIN tb_team tt ON tt.tm_pk_id = tb_slots.sl_fk_tm_pk_id
WHERE sl_week_num = ?
ORDER BY sl_slot_num"""

    week = process_week(week)
    return {week: {"slots": _db_read(q_slots, (week,))}}


class Manage:
    @classmethod
    def load_dash(cls, week):
        week = process_week(week)
        return {
            "sel_week": week,
            "max_week": process_week(),
            "slots": get_slots_data(week)[week]["slots"],
            "scores": get_scores_data(week)[week]["scores"],
            "teams": [[str(team[0]), team[1]] for team in cls.get_teams()]
        }

    @staticmethod
    def get_teams(ind=None):
        q = """
        SELECT tm_pk_id, tm_name, tm_dp_path, 
        FROM tb_team
        ORDER BY tm_name"""
        q_sel = " WHERE tm_pk_id = ?"

        if ind is not None:
            q += q_sel

        return _db_read(q, (ind,) if ind else ())

    class Modify:
        q_scores_update = '''
        '''
        q_scores_delete = 'DELETE FROM tb_slots WHERE sl_week_num = ? AND sl_slot_num = ? AND sl_fk_tm_pk_id = ?'
        q_scores_add = """INSERT INTO tb_slots ()"""

        @classmethod
        def test_endpoint(cls, task, data):
            print("task: " + str(task))
            print("data: " + str(data))

            if task == "modify_slots":
                if data.get("action") == "delete":
                    week = data.get("data").get("week")
                    slot = data.get("data").get("slot")
                    team_id = data.get("data").get("team_id")
                    print("slot: {} & team_id: {} & week: {}".format(slot, team_id, week))
                    _db_write(cls.q_scores_delete, (week, slot, team_id))
                    return True

            return "OK"
