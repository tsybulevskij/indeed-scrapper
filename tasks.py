from celery import Celery
from sqlalchemy.orm import sessionmaker

from models import db_connect, JobInfo, create_table
from job_scrapy.settings import BROKER_URL, CELERY_RESULT_BACKEND

app = Celery('tasks', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)


def add_filter_salary(data, instance, query, session):
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

@app.task
def insert_item(item):
    engine = db_connect()
    create_table(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for data in item:
        job = JobInfo(**data)
        if data['sponsored']:
            exist_row = session.query(JobInfo).filter(
                JobInfo.title == data['title'],
                JobInfo.sponsored == data['sponsored']
            ).all()
            if not exist_row:
                session.add(job)
                session.commit()
            else:
                query = session.query(JobInfo).filter(
                    JobInfo.title == data['title'],
                    JobInfo.sponsored == data['sponsored']
                )
                for instance in query:
                    add_filter_salary(data, instance, query, session)

        if data['sponsored'] is None:
            exist_post_url = session.query(JobInfo).filter(JobInfo.post_url == data['post_url']).all()
            if not exist_post_url:
                session.add(job)
                session.commit()
            else:
                query = session.query(JobInfo).filter(JobInfo.post_url == data['post_url'])
                for instance in query:
                    add_filter_salary(data, instance, query, session)
    session.close()
