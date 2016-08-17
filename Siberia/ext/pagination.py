__author__ = 'spouk'
__all__ = ("Paginarion",)


import asyncio
from sqlalchemy import select, func, between

LINKS_TEMPLATE = """<style>
      div.pagination {
              text-align:center;
              padding: 7px;
              margin: 3px;
      }
      %s
    </style>

<div class="pagination">
    %s
</div>
"""
DEFAULT_STYLE = """div.pagination a {
              padding: 2px 5px 2px 5px;
              margin: 2px;
              border: 1px solid #000000;

              text-decoration: none; /* no underline */
              color: #000000;
      }
      div.pagination a:hover, div.pagination a:active {
              border: 1px solid #000000;
              background-color:#000000;
              color: #fff;
      }
      div.pagination span.active {
              padding: 2px 5px 2px 5px;
              margin: 2px;
                      border: 1px solid #000000;

                      font-weight: bold;
                      background-color: #000000;
                      color: #FFF;
              }
      div.pagination span.disabled {
                      padding: 2px 5px 2px 5px;
                      margin: 2px;
                      border: 1px solid #EEE;
                      color: #DDD;
              }
      div.pagination > .active {
            background-color: lightgrey;
        }
        div.pagination > .passive {
            background-color: white;
        }
        div.pagination> .disabled {
            pointer-events: none;
            cursor: default;
        }
"""
START_LINK = """<a class="%s" href="{{ url_for('%s', parts={'p':'%s'}) }}"> < </a>"""
PAGE_LINK = """<a class="%s" href="{{ url_for('%s', parts={'p':'%s'}) }}"> %s </a>"""
END_LINK = """<a class="%s" href="{{ url_for('%s', parts={'p': '%s'}) }}"> > </a>"""

# вариант с request.path - выкидываем рендер нинзя  и 1 карутину
# START_LINK = """<a class="%s" href="%s?page=%s"> < </a>"""
# PAGE_LINK = """<a class="%s" href="%s?page=%s"> %s </a>"""
# END_LINK = """<a class="%s" href="%s?page=%s"> > </a>"""


class Pagination:
    COUNT_LINKS = 3

    def __init__(self, app, table, page, countonpage, db, namerouter, defaultstyle=True):
        self.app = app
        self.defaultstyle = defaultstyle
        self.table = table
        self.db = db
        self.page = page
        self.countonpage = countonpage
        self.name = namerouter
        self.records = None
        self.result = None
        self.records_count = None
        self.random_obj = None

    def init(self, page, namerouter, table=None, random_obj=None):
        self.random_obj = random_obj
        self.table = table
        self.page = page
        self.name = namerouter

    @asyncio.coroutine
    def runer_random_obj(self):
        yield from self.realpaginate_random_obj(random_obj=self.random_obj, page=self.page, count=self.countonpage)
        yield from self.paginatelinks()

    @asyncio.coroutine
    def runer(self):
        if self.random_obj:
            yield from self.realpaginate_random_obj(random_obj=self.random_obj, page=self.page, count=self.countonpage)
            self.random_obj = None
        else:
            yield from self.realpaginate(table=self.table, page=self.page, count=self.countonpage)
        yield from self.paginatelinks()

    @asyncio.coroutine
    def count_table(self,table, conn):
        """возвращает общее количество записей в таблице для формирования списка линков """
        result = yield from(yield from conn.execute(select([func.count()]).select_from(table))).fetchone()
        return result[0]

    @asyncio.coroutine
    def record_on_page(self, conn, table, page, count_on_page):
        """возвращает лимит записей по критериям  - страница/количество_на_страницу"""
        page = page < 0 and 1 or page
        records = yield from(yield from conn.execute(table.select().limit(count_on_page).offset((page-1)*count_on_page))).fetchall()
        return records

    @asyncio.coroutine
    def realpaginate_random_obj(self, random_obj, page, count):
        """обсчитывает границы """
        if random_obj:

            # total pages * count
            self.totalpages, ostatok = divmod(len(random_obj), count)
            self.totalpages  = ostatok and self.totalpages + 1 or self.totalpages
            print("Totalpage:", self.totalpages, ostatok)
            if self.totalpages == 0:
                self.totalpages = 1

            if isinstance(page, str):
                page = int(page)

            page = page < 1 and 1 or page
            if page > self.totalpages:
                page = self.totalpages - 1
            if page < 1 or page == 0:
                page = 1

            if page == 1 or page == 0:
                start = 0
            else:
                start = page * count

            end = start + count

            self.page = page
            self.records = random_obj[start:end]
            return random_obj

    @asyncio.coroutine
    def realpaginate(self, table, page, count):
        """обсчитывает границы """
        with (yield from self.db) as conn:
            # select all
            self.records_count = yield from self.count_table(table, conn)
            # total pages * count
            if self.records_count:
                self.totalpages, ostatok = divmod(self.records_count, count)
                self.totalpages  = ostatok and self.totalpages + 1 or self.totalpages
                if self.totalpages == 0:
                    self.totalpages = 1

                if isinstance(page, str):
                    page = int(page)

                page = page < 1 and 1 or page
                if page > self.totalpages:
                    page = self.totalpages - 1
                if page < 1:
                    page = 1

                page = int(page) < 1 and 1 or int(page)
                if page > self.totalpages:
                    page = self.totalpages - 1
                if page < 1 or page == 0:
                    page = 1
                self.page = page
                self.records = yield from self.record_on_page(conn=conn,table=table,page=self.page,count_on_page=count)
                return list(self.records)

    @asyncio.coroutine
    def paginatelinks(self):
        """ формирование результата """
        plinks = []
        res = []
        # формирую линки по количеству страниц показываемых между крайними значениями
        st = None
        if self.totalpages == 1:
            st = 1
        elif self.totalpages > 1:
            st = 0

        for x in range(st, self.totalpages + 1 ):
            plinks.append(PAGE_LINK % (self.page==x and "active" or "passive", self.name, x, x))
        # if self.totalpages  <= self.COUNT_LINKS  = показывается все, start, end = disabled
        if self.totalpages <= self.COUNT_LINKS:
            start = START_LINK % ('disabled', self.name, self.page)
            if self.page < self.totalpages - 1:
                end = END_LINK % ('', self.name, self.page  + 1)
            else:
                end = END_LINK % ('disabled', self.name, self.page)

        # if self.totalpages > self.COUNT_LINKS
        if self.totalpages > self.COUNT_LINKS:

            if self.totalpages - self.page >= self.COUNT_LINKS:
                plinks = plinks[self.page:self.page + self.COUNT_LINKS]
            else:
                plinks = plinks[self.totalpages - self.COUNT_LINKS:]

            if self.page == 1:
                start = START_LINK % ('disabled', self.name, self.page)
                end = END_LINK % ('', self.name, self.page  + 1)
            if self.page > 1:
                start = START_LINK % ('', self.name, self.page - 1)
                if self.totalpages == self.page:
                    end = END_LINK % ('disabled', self.name, self.page)
                else:
                    end = END_LINK % ('', self.name, self.page  + 1)

        res.append(start)
        res.append(''.join(plinks))
        res.append(end)
        r = yield from self.jinja_rend(stroka=''.join(res))
        self.result = LINKS_TEMPLATE % (self.defaultstyle and DEFAULT_STYLE or '', r)

    @asyncio.coroutine
    def jinja_rend(self, stroka):
        res = yield from self.app.render(stroka, _string=True)
        return res

    def result_func(self):
        """обертка над представлением результата"""
        return self.result, self.records

