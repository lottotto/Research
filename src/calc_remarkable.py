from datetime import datetime


def C_or_D(param):
    if param == 'C' or param == 'D':
        return True
    else:
        return False


#熱中症リスクの計算
def WBGT(tmp, hum):
    WBGT = 0.735*tmp+0.0374*hum+0.00292*tmp*hum
    if WBGT >= 31:
        return "暑さ指数:{.1f} ({})".format(WBGT,"危険")
    elif WBGT >=28:
        return "暑さ指数:{.1f} ({})".format(WBGT,"厳重警戒")
    elif WBGT >= 25:
        return "暑さ指数:{.1f} ({})".format(WBGT,"警戒")
    elif WBGT >= 21:
        return "暑さ指数:{.1f} ({})".format(WBGT, "注意")
    else:
        pass
#Cf 環境省熱中症予防情報サイト, http://www.wbgt.env.go.jp/wbgt_detail.php 11月26日閲覧


#水不足リスクの計算
def lack_of_water_risk(tmp, hum, drink_water):
    if tmp >= 30 and hum <=40 and C_or_D(drink_water):
        return "水消費量増大リスク"

#感染症リスクの計算
def infection_risk(tmp, hum, co2, infect_number):
    if tmp <= 20 and hum <= 40 and infect_number:
        # if co2 >= 800:　#換気されていないと判断
        #     return "感染症蔓延リスク高"
        # else:
        return "感染症蔓延リスクあり"
# Cf 室温・湿度管理でインフル予防　20度以上、50～60％が理想｜ヘルスＵＰ｜NIKKEI STYLE
# https://style.nikkei.com/article/DGXKZO93955790T11C15A1W13001 11月26日閲覧


#睡眠不足リスクの計算
def lack_of_sleep_risk(tmp, sleep_items, lux):
    if tmp <= 15 and lux > 400 and C_or_D(sleep_items):
        return "睡眠不足リスクあり"
#路上寝泊まりの実体験から。府中市10月28日、寒くてほぼ寝れず。当時気温は15度ほど


#トイレのリスク
def toilet_risk(domestic_water, cleaning_toilet, sewage, geri, vomit):
    if C_or_D(domestic_water) and C_or_D(cleaning_toilet) and C_or_D(sewage):
        # if geri and vomit:
        #     return "トイレのリスク高"
        # else:
        return "トイレのリスクあり"


#調査できているかのリスク
def research_info_risk(questionnaire_strtime):
    questionnaire_dt = datetime.strptime(questionnaire_strtime, "%Y-%m-%d-%H:%M:%S")
    if datetime.now() - questionnaire_dt > datetime.timedelta(days=2):
        return "情報収拾不安定リスクあり"
