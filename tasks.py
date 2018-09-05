from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from models import db_connect, JobInfo, create_table

from job_scrapy.settings import BROKER_URL

app = Celery('tasks', broker=BROKER_URL)

@app.task
def insert_item(item):
    engine = db_connect()
    create_table(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for data in item:
        job = JobInfo(**data)
        try:
            session.add(job)
            session.commit()
        except IntegrityError:
            session.rollback()
            query = session.query(JobInfo).filter(JobInfo.post_url == data['post_url'])
            for instance in query:
                if instance.filter_salary is not None:
                    salaries = instance.filter_salary.split(';')
                    if data['filter_salary'] and data['filter_salary'] not in salaries:
                        query.update(
                            {
                                JobInfo.filter_salary: JobInfo.filter_salary + ';' + data['filter_salary']
                            },
                            synchronize_session='fetch'
                        )
                        session.commit()
        finally:
            session.close()
