import unittest
from scripts.collect import weekly

class WeeklyTests(unittest.TestCase):
    def test_monday_boundary_and_casefold(self):
        rows=[{'createdAt':'2026-11-22T23:59:59Z','requester':'0xAb'},
              {'createdAt':'2026-11-23T00:00:00Z','requester':'0xAB'},
              {'createdAt':'2026-11-23T02:00:00Z','requester':'0xab'},
              {'createdAt':'2026-11-24T00:00:00Z','requester':'0xcd'}]
        a,b=weekly(rows)
        self.assertEqual(a['week'],'2026-11-16')
        self.assertEqual(b,{'week':'2026-11-23','tasks':3,'posters':2,'largestPosterTasks':2,'top5Tasks':3})
    def test_timezone_normalizes_to_utc(self):
        self.assertEqual(weekly([{'createdAt':'2026-11-22T20:00:00-05:00','requester':'a'}])[0]['week'],'2026-11-23')
    def test_top_five_excludes_sixth(self):
        rows=[{'createdAt':'2026-11-23T00:00:00Z','requester':str(i)} for i in range(6)]
        self.assertEqual(weekly(rows)[0]['top5Tasks'],5)
    def test_empty_history(self):
        self.assertEqual(weekly([]),[])

if __name__=='__main__': unittest.main()
