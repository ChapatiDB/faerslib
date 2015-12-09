import sqlite3
import drugstandards as drugs

class FAERS:
    def __init__(self, filename, countries=["UNITED STATES"], years="*"):
        """ This method is used to establish a connection 
            with an existing FAERS database.
        """
        self.conn = sqlite3.connect(filename)

        if type(countries) != list: countries = [countries]
        if type(years) != list: years = [years]

        self.countries = [i.upper() for i in countries]
        self.years = [str(i) for i in years]

        try:
            if self.countries[0] == "*": countries = "%%"
        except:
            pass
        try:
            if self.years[0] == "*": years = ["%"]
        except:
            pass
        years = " OR EVENT_DT LIKE ".join(["'{0}%'".format(i) for i in years])
        countries = " OR REPORTER_COUNTRY LIKE ".join(["'%{0}%'".format(i) for i in countries])
        years_exist = self.conn.execute("SELECT COUNT(*) FROM DEMO WHERE EVENT_DT LIKE %s" % years).fetchone()[0]
        if years_exist:
            # Join DRUG with DRUG_MAP into STANDARD_DRUG (ISR, DRUGNAME) using only records from 'countries' and 'years'
            sql = "CREATE TEMP TABLE STANDARD_DRUG AS SELECT ISR, REPLACEMENT AS DRUGNAME FROM DRUG INNER JOIN DRUG_MAP ON (DRUG.DRUGNAME = DRUG_MAP.ORIGINAL) WHERE ISR IN (SELECT ISR FROM DEMO WHERE REPORTER_COUNTRY LIKE %s AND EVENT_DT LIKE %s)" % (countries, years)
            self.conn.execute(sql)
            # Create DRUG_EVENT_COUNT table 
            sql = "CREATE TEMP TABLE DRUG_EVENT_COUNT AS SELECT DRUGNAME, PT, COUNT(DISTINCT(ISR)) AS COUNT FROM temp.STANDARD_DRUG INNER JOIN REAC USING (ISR) GROUP BY ISR, DRUGNAME, PT"
            self.conn.execute(sql)
            self.conn.execute("CREATE INDEX temp.drug_event_count_idx ON DRUG_EVENT_COUNT (DRUGNAME, PT, COUNT)")
            records = self.conn.execute("SELECT SUM(COUNT) FROM temp.DRUG_EVENT_COUNT").fetchone()[0]
            self.records = records
        else:
            pass
        print "*"*50
        print "Using records from:"
        print "  Countries : ", ", ".join(self.countries)
        print "  Years : ", ", ".join(self.years)
        print "  Total records : ", self.records
        print "*"*50

    def show_top_countries(self,n):
        """ This method will return list of countries sorted by the number of 
            records found.
        """
        result = self.conn.execute("SELECT REPORTER_COUNTRY, COUNT(DISTINCT(ISR)) as COUNT FROM DEMO GROUP BY REPORTER_COUNTRY ORDER BY COUNT DESC LIMIT %s" % str(n)).fetchall()
        return [[str(k),v] for k,v in result]

    def drug_event_stats(self, drug, event):
        """ This method computes frequencies used in calculating the PRR:
            Freq event | drug: the frequency that event is found with drug.
            Freq anyevent | drug: the frequency that any event is associated with drug.
            Freq event | other drugs: the frequency that the event is observed with all other drugs.
            Freq anyevent | other drugs: the frequnecy that any event is assciated with all other drugs.
        """
        drug = drugs.standardize([drug])[0]
        event = event.upper()
        event_drug = "SELECT SUM(COUNT) FROM DRUG_EVENT_COUNT WHERE DRUGNAME = \"%s\" AND PT = \"%s\"" % (drug, event)
        anyevent_drug = "SELECT SUM(COUNT) FROM DRUG_EVENT_COUNT WHERE DRUGNAME = \"%s\"" % (drug)
        event_otherdrugs = "SELECT SUM(COUNT) FROM DRUG_EVENT_COUNT WHERE DRUGNAME <> \"%s\" AND PT = \"%s\"" % (drug, event)
        anyevent_otherdrugs = "SELECT SUM(COUNT) FROM DRUG_EVENT_COUNT WHERE DRUGNAME <> \"%s\"" % (drug)
        event_drug = self.conn.execute(event_drug).fetchone()[0]
        anyevent_drug = self.conn.execute(anyevent_drug).fetchone()[0]
        event_otherdrugs = self.conn.execute(event_otherdrugs).fetchone()[0]
        anyevent_otherdrugs = self.conn.execute(anyevent_otherdrugs).fetchone()[0]
        drug_terms = self.conn.execute("SELECT DRUGNAME FROM temp.DRUG_EVENT_COUNT WHERE DRUGNAME = \"%s\" GROUP BY DRUGNAME" % drug).fetchall()
        drug_terms = [str(i[0]) for i in drug_terms]
        event_terms = self.conn.execute("SELECT PT FROM temp.DRUG_EVENT_COUNT WHERE PT = \"%s\" GROUP BY PT" % event).fetchall()
        event_terms = [str(i[0]) for i in event_terms]
        return {"drug_terms":drug_terms, "event_terms":event_terms, "event_drug":event_drug, "anyevent_drug":anyevent_drug, "event_otherdrugs":event_otherdrugs, "anyevent_otherdrugs":anyevent_otherdrugs}

    def prr(self, drug, event):
        """ This method calculates the Proportional Reporting Ratio (PRR) of a given
            drug-event pair.
        """
        result = self.drug_event_stats(drug, event)
        try:
            prr = (result["event_drug"]/float(result["anyevent_drug"])) / (result["event_otherdrugs"]/float(result["anyevent_otherdrugs"]))
        except:
            prr = None
        result["proportional_reporting_ratio"] = prr
        return result

    def associated_events(self, drugname, sortby="COUNT"):
        """ This method will return a sorted list of drug-event frequencies.
        """
        drugname = drugs.standardize([drugname])[0]
        sql = "SELECT DRUGNAME, PT, COUNT FROM temp.DRUG_EVENT_COUNT WHERE DRUGNAME = '%s' ORDER BY %s DESC" % (drugname, sortby)
        results = self.conn.execute(sql).fetchall()
        return [[str(k),str(v),c] for k,v,c in results]
    
    def associated_drugs(self, event, sortby="COUNT"):
        """ This method will return a sorted list of event-drug frequencies.
        """
        sql = "SELECT PT AS EVENT, DRUGNAME, COUNT FROM temp.DRUG_EVENT_COUNT WHERE PT = '%s' ORDER BY %s DESC" % (event.upper(), sortby)
        result = self.conn.execute(sql).fetchall()
        return [[str(k), str(v), c] for k,v,c in result]

    def drug_counts(self, sortby="COUNT"):
        """ This method will return a sorted list of drug frequencies.
        """
        sql = "SELECT DRUGNAME, COUNT(*) AS COUNT FROM DRUG GROUP BY ISR, DRUGNAME ORDER BY %s DESC" % sortby
        results = self.conn.execute(sql).fetchall()
        return results
        print len(results)
        print len(results[0])
        return [[str(k),v] for k,v,m in results]

    def event_counts(self, sortby="COUNT"):
        """ This method wil return a sorted list of event frequencies.
        """
        sql = "SELECT PT AS EVENT, COUNT(*) AS COUNT FROM REAC GROUP BY ISR, PT ORDER BY %s DESC" % sortby
        results = self.conn.execute(sql).fetchall()
        return [[str(k),v] for k,v in results]

    def find_like_drugs(self, drug, sortby="COUNT"):
        """ Return a list of all similar drug names.
        """
        sql = "SELECT DRUGNAME, COUNT(DISTINCT(ISR)) AS COUNT FROM DRUG WHERE DRUGNAME LIKE '%%%s%%'  GROUP BY DRUGNAME ORDER BY %s DESC" % (drug.upper(), sortby)
        results = self.conn.execute(sql).fetchall()
        return [[str(k),v] for k,v in results]

    def find_like_events(self, event, sortby="COUNT"):
        """ Return a list of all similar event names.
        """
        sql = "SELECT PT, COUNT(DISTINCT(ISR)) AS COUNT FROM REAC WHERE PT LIKE '%%%s%%' GROUP BY PT ORDER BY %s DESC" % (event.upper(), sortby)
        result = self.conn.execute(sql).fetchall()
        return [[str(k),v] for k,v in result]

    def mine_prr_by_drug(self, drug, n=3):
        """ Given a drug, compute PRR for all events assocated with drug for 
            drug-event with frequency >= n.
        """
        drug = drugs.standardize([drug])[0]
        sql = "SELECT PT FROM temp.DRUG_EVENT_COUNT WHERE DRUGNAME = '%s' AND COUNT >= %s" % (drug, str(n))
        result = self.conn.execute(sql)
        events = [str(i[0]) for i in result]
        prr_list = [self.prr(drug, e) for e in events]
        prr_list = [i for i in prr_list if i['proportional_reporting_ratio'] != None]
        idx = sorted(range(len(prr_list)), key = lambda k: -prr_list[k]['proportional_reporting_ratio'])
        prr_list = [prr_list[i] for i in idx]
        return prr_list

    def mine_prr_by_event(self, event, n=3):
        """ Given an event, compute PRR for all drugs associated with event for
            drug-event pairs with frequency >= n.
        """
        sql = "SELECT DRUGNAME FROM temp.DRUG_EVENT_COUNT WHERE PT = \"%s\" AND COUNT >= %s" % (event, str(n))
        result = self.conn.execute(sql)
        drugs = [str(i[0]) for i in result]
        prr_list = [self.prr(d, event) for d in drugs]
        prr_list = [i for i in prr_list if i['proportional_reporting_ratio'] != None]
        idx = sorted(range(len(prr_list)), key=lambda k: -prr_list[k]['proportional_reporting_ratio'])
        prr_list = [prr_list[i] for i in idx]
        return prr_list
        
