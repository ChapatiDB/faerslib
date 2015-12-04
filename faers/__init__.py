import sqlite3
import drugstandards as drugs

class FAERS:
    def __init__(self, filename):
        """ This method is used to establish a connection 
            with an existing FAERS database.
        """
        self.conn = sqlite3.connect(filename)
    
    def get_drug_event_stats(self, drug, event):
        """ This method will return the following:
            Freq(event | drug): Number of reports of drug causing event.
            Freq(all_events | drug): Number of reports of any side effect given drug.
            Freq(event | other_drugs): Number of reports of any drug causing side effect.
            Freq(all_events | other_drugs): Number of reports for any event among all other drugs.
        """
        drug = drugs.standardize([drug])[0]
        event = event.upper()
        event_drug = "SELECT COUNT(*) FROM EVENT WHERE PT LIKE '%s' AND DRUGNAME LIKE '%s'" % (event, drug)
        allevents_drug = "SELECT COUNT(*) FROM EVENT WHERE DRUGNAME LIKE '%s'" % drug
        event_otherdrugs = "SELECT COUNT(*) FROM EVENT WHERE PT LIKE '%s' AND DRUGNAME NOT LIKE '%s'" % (event, drug)
        allevents_otherdrugs = "SELECT COUNT(*) FROM EVENT WHERE DRUGNAME NOT LIKE '%s'" % (drug)
        return {"event_drug":event_drug, "allevents_drug":allevents_drug, "event_otherdrugs":event_otherdrugs, "allevents_otherdrugs":allevents_otherdrugs}

    def prr(self, drug, event):
        """ This method wil return the proportional-reporting-ratio (PRR)
            for a given drug-reaction pair.
        """
        stats = self.get_drug_event_stats(drug, event)
        return ((stats["event_drug"]/float(stats["allevents_drug"])) / (stats["event_otherdrugs"]/float(stats["allevents_otherdrugs"])))
        
    def common_events(self, drug):
        """ This method will return a list of most common drug-event pairs sorted
            by frequency.
        """
        drugname = drugs.standardize([drug])[0]
        sql = "SELECT DRUGNAME, PT, COUNT(*) AS COUNT FROM EVENT WHERE DRUGNAME = '%s' GROUP BY DRUGNAME, PT ORDER BY COUNT" % drug.upper()
        results = self.conn.execute(sql).fetchall()
        return [[i,j] for i,j in results]

