# Monitoramento OLT ZTE
##### Zabbix 5.4 +
##### ZTE C300 


#### Faça a instalação das dependencias necessárias

```sh
apt update
apt install git snmp python3 zabbix-sender -y

```
#### Baixe os arquivos .py e os coloque em: /usr/lib/zabbix/externalscripts/

```sh
cd /tmp
git clone https://github.com/odouglasrodrigues/template-olt-zte.git
cd template-olt-zte
mv *.py /usr/lib/zabbix/externalscripts/


```

##### Dê permissão de execução:
#
```sh
chmod +x /usr/lib/zabbix/externalscripts/*.py
```
#
##### Crie o arquivo de agendamento, dê permissão e reinicie o cron:
#
```sh
sudo echo "#ARQUIVO PARA AGENDAMENTO TEMPLATE OLT">/etc/cron.d/TemplateOLT
sudo chown root /etc/cron.d/TemplateOLT
sudo chmod 644 /etc/cron.d/TemplateOLT
service cron restart
```
##### Coloca o usuário zabbix no arquivo de sudoers sem necessiade de senha:
#
```sh
sudo echo "zabbix ALL=NOPASSWD: ALL">> /etc/sudoers
```
#



## License

MIT

**!**
