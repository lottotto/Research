import datetime

class CalcRemarkProblem():
    def __init__(self, mongo_document):

        #値抜けの可能性あるので、dict.get(key)で値を抽出
        self.document = mongo_document
        self.sensor = mongo_document.get('sensor') #Noneメソッドは.getを持たないので、一度これを挟む
        if self.sensor is not None:
            self.tmp = float(self.sensor['tmp'])
            self.hum = float(self.sensor['hum'])
            self.lux = int(self.sensor['lux'])
            self.co2 = int(self.sensor['co2'])
        else:
            self.tmp = None
            self.hum = None
            self.lux = None
            self.co2 = None

    #熱中症リスクの計算

    def C_or_D(self, param):
        if param == 'C' or param == 'D' or param == "0":
            return True
        else:
            return False

    def is_None(self, *args):
        if None in args:
            return True
        else:
            False

    def WBGT(self):
        if self.is_None(self.tmp, self.hum) == True:
            return "特になし"
        WBGT = 0.735*self.tmp+0.0374*self.hum+0.00292*self.tmp*self.hum
        if WBGT >= 31:
            return "暑さ警戒度:{}".format("危険")
        elif WBGT >=28:
            return "暑さ警戒度:{}".format("厳重警戒")
        elif WBGT >= 25:
            return "暑さ警戒度:{}".format("警戒")
        elif WBGT >= 21:
            return "暑さ警戒度:{}".format("注意")
        else:
            return "特になし"
    #Cf 環境省熱中症予防情報サイト, http://www.wbgt.env.go.jp/wbgt_detail.php 11月26日閲覧


    #水不足リスクの計算
    def lack_of_water_risk(self):
        drink_water=self.document.get('il01')
        if self.is_None(self.tmp, self.hum, drink_water) == True:
            return "特になし"
        if self.tmp >= 30 and self.hum <=40 and self.C_or_D(drink_water):
            return "水消費量増大リスク"
        else:
            return "特になし"

    #感染症リスクの計算
    def infection_risk(self):
        if self.is_None(self.tmp, self.hum, self.co2) == True:
            return "特になし"
        None_filter = lambda x:x is not None
        temp_list = [self.document.get('sp0'+str(x+1)) for x in range(4)] + [self.document.get('vi0'+str(x+1)) for x in range(3)]
        #temp_list = list(map(int, temp_list))
        temp_list = list(filter(None_filter, temp_list))
        infect_number = sum(list(map(int, temp_list)))

        if self.tmp <= 20 and self.hum <= 40 and infect_number:
            return "感染症蔓延リスクあり"
        else:
            return "特になし"
    # Cf 室温・湿度管理でインフル予防　20度以上、50～60％が理想｜ヘルスＵＰ｜NIKKEI STYLE
    # https://style.nikkei.com/article/DGXKZO93955790T11C15A1W13001 11月26日閲覧


    #睡眠不足リスクの計算
    def lack_of_sleep_risk(self):
        sleep_items = self.document.get('en02')
        if self.is_None(self.tmp, self.lux, sleep_items) == True:
            return "特になし"
        elif self.tmp <= 15 and self.lux > 400 and self.C_or_D(sleep_items):
            return "睡眠不足リスクあり"
        else:
            return "特になし"
    #路上寝泊まりの実体験から。府中市10月28日、寒くてほぼ寝れず。当時気温は15度ほど


    #トイレのリスク
    def toilet_risk(self):
        domestic_water = self.document.get('il06')
        cleaning_toilet= self.document.get('il03')
        sewage         = self.document.get('en07')
        if self.is_None(domestic_water, cleaning_toilet, sewage) == True:
            return "特になし"
        if self.C_or_D(domestic_water) and self.C_or_D(cleaning_toilet) and self.C_or_D(sewage):
            return "トイレのリスクあり"
        else:
            return "特になし"


    #調査できているかのリスク
    def research_info_risk(self):
        format_datetime = "%Y-%m-%d-%H:%M:%S"
        now_date = self.document.get('date')
        previous_date = self.document.get('previous_date')
        if previous_date is None:
            return '特になし'
        now_date_dt = datetime.datetime.strptime(now_date, format_datetime)
        previous_date_dt = datetime.datetime.strptime(previous_date,format_datetime)
        if now_date_dt - previous_date_dt > datetime.timedelta(days=2):
            return "情報収拾不安定リスクあり"
        else:
            return "特になし"

    def run(self):
        ret_list = []
        ret_list.append(self.WBGT())
        ret_list.append(self.lack_of_water_risk())
        ret_list.append(self.infection_risk())
        ret_list.append(self.lack_of_sleep_risk())
        ret_list.append(self.toilet_risk())
        ret_list.append(self.research_info_risk())
        ret_list = list(set(ret_list))#特になしの重複を削除し、残った特になしを削除
        ret_list.remove('特になし')
        return ret_list
