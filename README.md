# 단순 이동평균선 시스템 트레이딩

단순 이동평균선을 이용해 비트코인을 거래하면 알려주는 텔레그램 봇

[비트코인 매매일지 (2021년 7월 21일 ~ 2021년 10월 22일)](https://docs.google.com/spreadsheets/d/1IIvGJcb1WXR74Eand_1pm64i5gxzQlwnCvGZxcpMo4k/edit?usp=sharing)

## 배포

시간대 설정

```bash
sudo dpkg-reconfigure tzdata
```

패키지 설치

```bash
sudo apt update && sudo apt upgrade -y
```

```bash
sudo apt install python3-pip -y
```

```bash
git clone https://github.com/yehwankim23/simple-moving-average-system-trading.git
```

```bash
pip3 install -r requirements.txt --upgrade
```

실행

```bash
vim main.py
```

```bash
nohup python3 main.py > output.log &
```
