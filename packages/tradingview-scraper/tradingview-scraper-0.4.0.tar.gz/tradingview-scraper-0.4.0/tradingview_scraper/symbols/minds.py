1- Scrape news headline from providers/symbols
2- Scrape news page content


https://www.tradingview.com/symbols/BTCUSD/minds/

curl 'https://www.tradingview.com/symbols/BTCUSD/minds/' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: en-US,en;q=0.9,fa;q=0.8' \
  -H 'cache-control: max-age=0' \
  -H 'cookie: cookiePrivacyPreferenceBannerProduction=notApplicable; _ga=GA1.1.305031130.1722620382; cookiesSettings={"analytics":true,"advertising":true}; device_t=Zk5BSzow.mMVL4kf2Tf695LpXGx8nn2LAZ_rw91Q4aJo68Z32kys; sessionid=gcbftwybvv8348jnxjv3xgr415yqv4ec; sessionid_sign=v3:Q8y+0F9z9/Ouw8bHcy65AXmioOACoTWdA+uTCiDD3CM=; tv_ecuid=7894f482-1e83-47dc-8522-6a03e12d7948; __gads=ID=7d27a3221f9e7d89:T=1723364743:RT=1724311243:S=ALNI_MaRJSJlKrl31YGtk1eP--c4buMPDA; __gpi=UID=00000ec1e925d00a:T=1723364743:RT=1724311243:S=ALNI_MZoaEB3uMyP70MxoA4UJn_UWIBloA; __eoi=ID=0af73439e9b04585:T=1723364743:RT=1724311243:S=AA-AfjaAWkSRFCERTq2s__Lhj8Gf; _sp_ses.cf1a=*; _sp_id.cf1a=21e49849-cc20-4c25-a635-d17dd80895b9.1722620380.20.1724483580.1724311339.ed8b5f15-3ad8-42c5-88e9-26e8841cb64e; _ga_YVVRYGL0E0=GS1.1.1724482859.23.1.1724483581.26.0.0' \
  -H 'priority: u=0, i' \
  -H 'referer: https://www.tradingview.com/symbols/BTCUSD/news/' \
  -H 'sec-ch-ua: "Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
  
  
API
https://www.tradingview.com/api/v1/minds/?c=ImMiOjEwLCJvIjoiLWlkIiwidiI6WzQ4OTMyMF0&f=symbol&symbol=BITSTAMP%3ABTCUSD&new_count=False
