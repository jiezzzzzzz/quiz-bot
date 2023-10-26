import json

import redis
from environs import Env


def read_koi_files(file_path, file_encoding='KOI8-R'):
    with open(file_path, 'r', encoding=file_encoding) as file:
        text = file.read()
        return text


def redis_load_question(redis_conn, hash_name='questions'):
    for text in read_koi_files():
        counter = redis_conn.hlen(hash_name)

        sections_text = text.split('\n\n')

        for section in sections_text:
            if section.strip().startswith('Вопрос'):
                question = ' '.join(section.strip().splitlines()[1:])
                continue

            if section.strip().startswith('Ответ'):
                answer = ' '.join(section.strip().splitlines()[1:])
                counter += 1
                redis_conn.hset(
                    hash_name,
                    f'question_{counter}',
                    json.dumps({'question': question, 'answer': answer})
                )


def main():
    env = Env()
    env.read_env()

    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_password = env('REDIS_PASSWORD')

    redis_conn = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        charset='utf-8',
        decode_responses=True
    )

    redis_load_question(redis_conn)


if __name__ == '__main__':
    main()
