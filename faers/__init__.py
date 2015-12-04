import sqlite3
import drugstandards as drugs

class FAERS:
    def __init__(self, filename):
        """ This method is used to establish a connection 
            with an existing FAERS database.
        """
        self.conn = sqlite3.connect(filename)
        
    def drug_event_stats(self, drug, event):
        """ This metho computes frequencies used in calculating the PRR:
            Freq event | drug: the frequency that event is found with drug.
            Freq anyevent | drug: the frequency that any event is associated with drug.
            Freq event | other drugs: the frequency that the event is observed with all other drugs.
            Freq anyevent | other drugs: the frequnecy that any event is assciated with all other drugs.
        """
        event_drug = "SELECT SUM(COUNT) FROM DRUG_EVENT_COUNT WHERE DRUGNAME LIKE '%%%s%%' AND PT LIKE '%%%s%%'" % (drug, event)
        anyevent_drug = "SELECT SUM(COUNT) FROM DRUG_EVENT_COUNT WHERE DRUGNAME LIKE '%%%s%%'" % (drug)
        event_otherdrugs = "SELECT SUM(COUNT) FROM DRUG_EVENT_COUNT WHERE DRUGNAME NOT LIKE '%%%s%%' AND PT LIKE '%%%s%%'" % (drug, event)
        anyevent_otherdrugs = "SELECT SUM(COUNT) FROM DRUG_EVENT_COUNT WHERE DRUGNAME NOT LIKE '%%%s%%'" % (drug)
        event_drug = self.conn.execute(event_drug).fetchone()[0]
        anyevent_drug = self.conn.execute(anyevent_drug).fetchone()[0]
        event_otherdrugs = self.conn.execute(event_otherdrugs).fetchone()[0]
        anyevent_otherdrugs = self.conn.execute(anyevent_otherdrugs).fetchone()[0]
        return {"event_drug":event_drug, "anyevent_drug":anyevent_drug, "event_otherdrugs":event_otherdrugs, "anyevent_otherdrugs":anyevent_otherdrugs}

    def prr(self, drug, event):
        """ This method calculates the Proportional Reportin Ratio (PRR) of a given
            drug-event pair.
        """
        drug = drugs.standardize([drug])[0]
        event = event.upper()
        result = self.drug_event_stats(drug, event)
        prr = (result["event_drug"]/float(result["anyevent_drug"])) / (result["event_otherdrugs"]/float(result["anyevent_otherdrugs"]))
        return prr

    def common_events(self, drugname, sortby="COUNT"):
        """ This method will return a sorted list of drug-event frequencies.
        """
        drugname = drugs.standardize([drugname])[0]
        sql = "SELECT DRUGNAME, PT, COUNT(*) AS COUNT FROM EVENT WHERE DRUGNAME = '%s' GROUP BY DRUGNAME, PT ORDER BY %s DESC" % (drugname.upper(), sortby)
        results = self.conn.execute(sql).fetchall()
        return [[str(k),str(v),c] for k,v,c in results]

    def drug_counts(self, sortby="COUNT"):
        """ This method will return a sorted list of drug frequencies.
        """
        sql = "SELECT DRUGNAME, COUNT(*) AS COUNT FROM EVENT GROUP BY DRUGNAME ORDER BY %s DESC" % sortby
        results = self.conn.execute(sql).fetchall()
        return results
        print len(results)
        print len(results[0])
        return [[str(k),v] for k,v,m in results]

    def event_counts(self, sortby="COUNT"):
        """ This method wil return a sorted list of event frequencies.
        """
        sql = "SELECT PT AS EVENT, COUNT(*) AS COUNT FROM EVENT GROUP BY PT ORDER BY %s DESC" % sortby
        results = self.conn.execute(sql).fetchall()
        return [[str(k),v] for k,v in results]

    def find_like_drugs(self, drug, sortby="COUNT"):
        """ Return a list of all similar drug names.
        """
        sql = "SELECT DRUGNAME, COUNT(*) AS COUNT FROM EVENT WHERE DRUGNAME LIKE '%%" + drug.upper() + "%%' GROUP BY DRUGNAME ORDER BY %s DESC" % sortby
        results = self.conn.execute(sql).fetchall()
        return [[str(k),v] for k,v in results]
