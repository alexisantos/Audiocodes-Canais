#!/usr/bin/env python 
# coding=UTF-8

#    Descrição:
#    Este script faz uma consulta SNMP para uma OID com o mapeamento dos canais do tronco E1 (acTrunkStatusChannels)
#    de Gateways AudioCodes Mediant 1000 e devolve parâmetros contábeis tais como:
#    canais em uso, canais bloqueados e canais livres.
#    Script para aplicação em Zabbix Server ou consulta individual em terminal linux (necessário pacote SNMP)

#    Autor: Alex Santos (IFRN)
#    Data:  27/12/2017

# De acordo com medições empíricas realizadas, existem dois padrões de exibição do uso dos canais no audiocodes:
#   1 quando não existem canais sem bloqueio
#   2 quando há canais com bloqueio
# Exemplos: 
#   1: 133C333313333333
#   2: 81 88 88 88 88 33 38 38 81 83 83 83 33 83 38 38

# Utilização
#  ./AudioCodes-ContaCanais.py <host_dns/host_ip> <comunidadeSNMP> <num_tronco> <parâmetro>

#  Parâmetros:
#      -c: exibe o mapeamento dos canais no tronco E1, no formato que o equipamento envia"
#      -l: retorna a quantidade de canais livres (sem ocupação)"
#      -u: retorna quantidade de canais em uso (ocupado com voz)"
#      -b: retorna quantidade de canais em bloqueio (ocupado com bloqueio de sinalização)"
#      -t: exibe todas as informações acima"

# Recomendação de discovery rule (Zabbix)
#   UserParameter=E1.CanaisInfo[*], <caminho_do_script>./AudioCodes-ContaCanais.py $1 $2 $3 $4

#   E1.CanaisInfo[{HOST.DNS},{$SNMP_COMMUNITY},{#SNMPINDEX},-l]
#   E1.CanaisInfo[{HOST.DNS},{$SNMP_COMMUNITY},{#SNMPINDEX},-u]
#   E1.CanaisInfo[{HOST.DNS},{$SNMP_COMMUNITY},{#SNMPINDEX},-b]

import sys
import subprocess

if (len(sys.argv) < 5):
  print subprocess.check_output("\n", shell=True)
  print "------------------------------------------------------------"
  print "  Contagem de canais do Audiocodes mediant 1000 ou similar"
  print "------------------------------------------------------------"
  print "  Utilização: " + str(sys.argv[0]) + " <host_dns/host_ip> <comunidadeSNMP> <num_tronco> <parâmetro>"
  print "  Parâmetros: "
  print "      -c: exibe o mapeamento dos canais no tronco E1, no formato que o equipamento envia"
  print "      -l: retorna a quantidade de canais livres (sem ocupação)"
  print "      -u: retorna quantidade de canais em uso (ocupado com voz)"
  print "      -b: retorna quantidade de canais em bloqueio (ocupado com bloqueio de sinalização)"
  print "      -t: exibe todas as informações acima"
  print subprocess.check_output("\n", shell=True)
  sys.exit()


host        = str(sys.argv[1])                                           # Audiocodes monitorado  mediant 1000
comunidade  = str(sys.argv[2])                                           # Comunidade SNMP do equipamento
oid         = '.1.3.6.1.4.1.5003.9.10.9.2.1.1.1.3.' + str(sys.argv[3])   # OID para o objeto acTrunkStatusChannels do mediant 1000
aspas       = '"'
linha       = '\n'

consultaSNMP = "snmpget -Ovq -v2c -c " + comunidade + " " + host + " " + oid
canais = subprocess.check_output(consultaSNMP, shell=True)
canais = canais.replace(aspas,"")
canais = canais.replace(linha,"")

if (canais.count(' ') == 0):              # Verifica o padrão é do tipo 2, observando se há espaços (" ") na variável canal
   A     = canais.count('A')
   B     = canais.count('B')
   C     = canais.count('C')
   D     = canais.count('D')
   em_uso   = canais.count('4') + A + C + D*2
   bloqueio = canais.count('8')
   livres   = 30 - em_uso - bloqueio
else:                                     # O padrão é do tipo 1
  if (canais == '1333333313333333'):      # Todos os canais estão livres
      livres   = 30
      bloqueio = 0
      em_uso   = 0  
  else:                                   # Faz a conagem de cada codificação
    bloqueio = canais.count('8')
    livres   = canais.count('3')
    em_uso   = canais.count('4')


# Imprimindo saida, conforme parâmetro recebido

if sys.argv[4] == '-b':
   print bloqueio

elif sys.argv[4] == '-l':
   print livres

elif sys.argv[4] == '-u':
   print em_uso

elif sys.argv[4] == '-t':
   print "Canais:    " + canais
   print "Livres:    " + str(livres)
   print "Em Uso:    " + str(em_uso)
   print "Bloquados: " + str(bloqueio)
elif sys.argv[4] == '-c':   
   print canais
else:     
  print "Falha!! Comando inválido!!"
  print subprocess.check_output(sys.argv[0], shell=True)

