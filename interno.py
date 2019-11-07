import node
import mensagem
import _thread
import tela
import time

# classe de ações internas do node
# resposta das mensagens de um nó
class Interno:

	def __init__(self,nod):
		self.app = None
		self.no = None
		if __name__ == "__main__":
			print("digite 0 para servidor ou 1 para cliente")
			# iniciando o servidor
			if int(input()) == 0 : 
				print("Digite a porta do servidor")
				#self.app = tela.Aplicativo(self, tela.TelaServidor)
				#self.app.mainloop()
				self.no = node.Node("",int(input()))
				self.no.servidor(self)
			# iniciando a tela do cliente
			else:
				#try :
				self.app = tela.Aplicativo(self)
				self.app.mainloop()
				# aplicativo encerrado
				if self.no.log : 
					self.no.next.send(self.no.msg.logout(self.no.next))
				#except: pass
				# cliente aguarda 5 segundos antes de fechar
				# para não derrubar os outros servidores
				# porém não é obrigatório
				time.sleep(2)
		else:
			self.no = nod
			
	
	# execute todas as mensagens recebidas
	# CRITICAL TODO
	def execute(self):
		while(len(self.no.msg.lista)):
			act = self.no.msg.lista.pop(0)
			self.answer(act[0],act[1])
	
	# responde uma mensagem
	def answer(self,next,jsn):
		ms = mensagem.Mensagem()
		
		# fazendo login
		if ms.isLogin(jsn):
			# validações do login
			try:
				nome = ms.getInJson(jsn,"nome")
				ip = ms.getInJson(jsn,"ip")
				porta = int(ms.getInJson(jsn,"porta"))
			except:
				print("dados incompreensíveis")
			if nome == -1 :
				self.alert(next,[1,0],"nome invalido para login",self.no.tipo==0) 	
				return False
			ind = self.existeUser(nome)
			if ind != -1:	
				self.alert(next,[1,0],"nome já esta sendo usado",self.no.tipo==0) 
				return False
			# ações no cliente
			if self.no.tipo :
				if ip == -1 or porta == -1:
					# cliente avisa servidor que deu um erro
					self.alert(next,[1,0],"ip ou porta inválida",self.no.tipo==0)
					return False
				# login pode ser feito
				#next.host = ip
				#next.port = porta	
			#next.nome = nome ;
			else:
				next.nome = nome 
			# confirmar
			self.alert(next,[1,1],"login realizado com sucesso",self.no.tipo==0)
			# enviando lista de online para o cliente
			if self.no.tipo == 0 :
				self.addNode(next)
				for cli in self.no.online:
					next.send(ms.login(cli))
				# finalização do login
			#if self.no.tipo == 0 :
				
				return True
			else:
				# atualiza tela
				n = node.Node(ip,porta,nome)
				self.addNode(n)
				try: self.app.tela_atual.reload()
				except: pass
				return True
				
		# fazendo logout
		if ms.isLogout(jsn):
			# validações
			nome = ms.getInJson(jsn,"nome")
			if nome == -1 :
				self.alert(next,[0,0],"nome invalido para logout",self.no.tipo==0)
				return False
			ind = self.existeUser(nome)
			if ind == -1:	
				self.alert(next,[1,0],"nome não existe na lista",self.no.tipo==0)
				return False
			# ação em um servidor
			if self.no.tipo == 0:
				self.alert(next,[0,1],"logout realizado com sucesso",self.no.tipo==0)
			# ação em um cliente
			#else:
				#print(next.nome,": está offline")
				# feedback desativado
			self.delNode(ind)  #next.nome = "cliente"
			# atualiza tela
			try: self.app.tela_atual.reload()
			except: pass
			return True
				
		# se for mensagem de confirmação
		if ms.isConfirm(jsn):
		
			# é uma confirmação de login?
			if ms.getInJson(jsn,"acao") == "1" :
				# ações no cliente
				if(self.no.tipo):
					if(ms.confLogin(jsn)):
						print("cliente logado, ir para tela principal")
						self.no.log = True
						self.app.trocarTela(tela.Menu)
						return True
					else:
						print("cliente não está logado")
						return False
				# ações no servidor
				else:
					return
			
			# é uma confirmação de logout?
			if ms.getInJson(jsn,"acao") == "0" :
				if ms.confLogout(jsn) :
					self.no.online = []
					self.no.log = False
					self.no.msg.lista = []
					print("Você fez logout")
					return True
		
		#se for mensagem de chat
		if ms.isMsg(jsn):
			remetente = ms.getInJson(jsn, "nomeenv")
			destinatario = ms.getInJson(jsn, "nomereceb")
			msg = ms.getInJson(jsn, "msg")

			#se a mensagem estiver errada
			if remetente == -1 or destinatario == -1 or msg == -1:
				return False
			
			# se for cliente
			if self.no.tipo :
				# deve adicionar na lista de mensagens do chat no next?
				next.msgChat.append([msg, "recebido"])
				print("cliente recebeu a msg", msg)
				self.app.tela_atual.mostra_msg(remetente, destinatario)
				return
			# se for servidor	
			else:
				#deve redirecionar a mensagem
				l = [i.nome for i in self.no.online]
				l = l.index(destinatario)
				l = self.no.online[l] #CRITICO
				l.send(jsn)
				print("o servidor repassou a mensagem", msg)
				return

			
		print(jsn,"não tratado") ; return True
		
		# aqui pode parar o algoritmo dos outros----------------------------------------------
		# self.alert(next,[0,0],"agindo de forma suspeita"); return False
	
	# alerta prox se permitido
	def alert(self,next,conf,msg,send=True):
		ms = mensagem.Mensagem()
		print(next.port,":",msg)
		if send : next.send(ms.confirm(conf[0],conf[1]))
	
	# verifica se já existe o usuário
	# CRÍTICO TODO
	def existeUser(self,nome):
		online = [ i.nome for i in self.no.online] 
		try: ind =  online.index(nome)
		except: ind = -1
		return ind
	
	# adiciona usuário na lista de onlines
	# CRÍTICO TODO
	def addNode(self,next):
		ms = mensagem.Mensagem()
		self.no.broadcast(ms.login(next))
		self.no.online.append(next)
		print("lista online:")
		for i in self.no.online:
			print("--> "+i.nome)
	
	# remove usuário da lista de onlines
	# CRITICO TODO
	def delNode(self,index):
		ms = mensagem.Mensagem()
		print("removendo",self.no.online[index].port)
		next = self.no.online.pop(index)
		self.no.broadcast(ms.logout(next)) 
		print("lista online:")
		for i in self.no.online:
			print("--> :",i.nome)

if __name__ == "__main__": 
	i = Interno(None)
