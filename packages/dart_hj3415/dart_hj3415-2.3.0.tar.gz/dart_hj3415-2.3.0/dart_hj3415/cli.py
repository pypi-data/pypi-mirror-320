import argparse
from dart_hj3415 import opendart
from db_hj3415 import mymongo, myredis

def save_today_darts(data_from_file=False) -> int:
    """
    오늘 공시 데이터를 수집해서 후처리후 몽고디비에 저장한다.
    :param data_from_file: 파일로 저장된 데이터를 사용한다.(디버깅용)
    :return: 저장된 총 공시개수 반환
    """
    if data_from_file:
        print(f"공시 데이터를 {opendart.OverView.SAVEFILENAME} 파일에서 가져옵니다.")
        import json
        # JSON 파일에서 리스트 불러오기
        with open(opendart.OverView.SAVEFILENAME, 'r') as file:
            overviews = json.load(file)
    else:
        overviews = opendart.OverView().get(save_to_file=True)
    print(f"총 {len(overviews)}의 데이터가 수집 되었습니다.")
    data = opendart.PostProcess.all_in_one(overviews)
    print("원본 데이터에서 후처리를 시행합니다...")

    # redis에 오늘 수집한 전체를 캐시로 저장
    myredis.DartToday().save(data)
    print(f"총 {len(data)}개의 공시를 redis_name : dart_today에 저장했습니다.")

    # mongodb에 각 종목별로 나눠서 저장
    for item in data:
        code = item['stock_code']
        name = item['corp_name']
        report_name = item['report_nm']
        print(f'{code}/{name}의 dart 테이블에 {report_name}공시를 저장합니다.')
        mymongo.Dart.save(code, item)
        print(f'\tredis_name : {code}_dart_get_recent_date를 갱신합니다.')
        myredis.Dart(code).get_recent_date(refresh=True)
    # pprint.pprint(data)
    print(f"총 {len(data)}개의 공시를 각 종목별로 mongodb에 저장했습니다.")
    return len(data)

def dart():
    parser = argparse.ArgumentParser(description="Dart Commands")
    command_subparsers = parser.add_subparsers(dest='command', help='명령어')

    # save 명령어 파서
    save_parser = command_subparsers.add_parser('save', help='dart 저장')
    save_parser.add_argument('-t', '--today', action='store_true', help='래디스 캐시를 사용하지 않고 강제로 재계산 할지')

    args = parser.parse_args()

    if args.command == 'save':
        if args.today:
            mymongo.Logs.save('cli','INFO', 'run >> dart save --today')
            save_today_darts()
    else:
        parser.print_help()
