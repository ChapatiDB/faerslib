import sqlite3
import drugstandards as drugs

class FAERS:
    def connect(self, filename):
        """ This method is used to establish a connection 
            with an existing FAERS database.
        """
        self.conn = sqlite3.connect(filename)
        
    def prr(self, drug, event):
        """ This method wil return the proportional-reporting-ratio (PRR)
            for a given drug-reaction pair.
        """
        drug = drugs.standardize([drug])[0]
        event = event.upper()
        n = int(self.conn.execute("SELECT COUNT(*) FROM EVENT WHERE DRUGNAME LIKE '%s' AND PT LIKE '%s'" % (drug, event)).fetchone()[0])
        m = float(self.conn.execute("SELECT COUNT(*) FROM EVENT WHERE DRUGNAME LIKE '%s' AND PT NOT LIKE '%s'" % (drug, event)).fetchone()[0])
        p = int(self.conn.execute("SELECT COUNT(*) FROM EVENT WHERE DRUGNAME NOT LIKE '%s' AND PT LIKE '%s'" % (drug, event)).fetchone()[0])
        q = float(self.conn.execute("SELECT COUNT(*) FROM EVENT WHERE DRUGNAME NOT LIKE '%s' AND PT NOT LIKE '%s'" % (drug, event)).fetchone()[0])
        return (n/m) / (p/q)

    def common_events(self, drugname):
        drugname = drugs.standardize([drugname])[0]
        sql = "SELECT DRUGNAME, PT, COUNT(*) AS COUNT FROM EVENT WHERE DRUGNAME = '%s' GROUP BY DRUGNAME, PT ORDER BY COUNT" % drugname.upper()
        results = self.conn.execute(sql).fetchall()
        return [[i,j] for i,j in results]

