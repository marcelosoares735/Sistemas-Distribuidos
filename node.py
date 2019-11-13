import socket
import _thread
import interno
import mensagem
import tela

# 10.40.1.60
# 10.20.8.182 meu ip
# cria um nó, seja ele cliente ou servidor
class Node:

	# configuração inicial
	def __init__(self,host="127.0.0.1", port = 22000, nome = "node"):
		self.host = host
		self.port = port
		self.nome = nome
		self.online = []
		self.con = None
		self.next = None
		self.intr = interno.Interno(self)
		self.msg = mensagem.Mensagem()
		self.log = False
		self.comunicando = False
		self.msgChat = []
		#self.myhost = 0
		#self.myport = 0
	
	# define nó como cliente
	# o intr permite alteração da parte "interna" do software
	def cliente(self, intr = None):
		if intr != None : self.intr = intr
		self.tipo = 1
		if not self.comunicando :	
			self.next = Node(self.host,self.port,self.nome)
			self.next.connect_with_servidor()
			self.next.intr=None
			_thread.start_new_thread(self.listening,())
	
	# thread para cliente sempre escutar servidor
	# TODO crítico
	def listening(self):
		while True:
			jsn = self.next.listen()
			if not jsn: break
			self.msg.add(self.next,	jsn)
			self.intr.execute()
		
		self.intr.app.tela_atual.reset()
		self.intr.app.trocarTela(tela.Login)
		#
	
	# define nó como servidor
	# o intr permite alteração da parte "interna" do software
	def servidor(self, intr = None):
		if intr : self.intr = intr
		self.host = ''
		self.tipo = 0
		self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.con.bind((self.host,self.port));
		self.con.listen(True)
		self.intr.app.trocarTela(tela.TelaServidor)
		print("Servidor iniciado.",socket.socket.getsockname(self.con)," Aguardando clientes.")
		
		while True:
			no = self.connect_with_client()
			print(no.port,": entrou no servidor")
			_thread.start_new_thread(self.servidor_talk,(no,))
	
	# nó cliente se conecta com nó servidor
	def connect_with_servidor(self):
		try:
			self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.con.connect((self.host,self.port))
			self.host,self.port = socket.socket.getsockname(self.con)
			self.comunicando = True
			print("comunicação com o servidor está estabelecida")
		except:
			self.comunicando = False
			print("Não foi possível estabelecer a comunicação")
	
	# nó servidor se conecta com um cliente
	def connect_with_client(self):
		con,dados = self.con.accept()
		no = Node(dados[0],dados[1])
		no.con = con
		return no
	
	# escuta um nó
	def listen(self):
		try: jsn = self.con.recv(1024).decode()
		except: jsn = ""
		
		print("<REC> ",jsn)
		return jsn
	
	# enviando para nó
	def send(self,jsn):
		jsn = jsn + '\n' # "\r\n"
		try: self.con.sendall(jsn.encode("UTF-8"))
		except: return
		print("<SND> ",jsn)
	
	# servidor conversando com nó
	def servidor_talk(self,next):
		next.intr = None
		while True:
			jsn = next.listen()
			self.intr.app.tela_atual.reload(jsn, "recebido: ")
			self.msg.add(next,jsn)
			if not jsn: break
			self.intr.execute()
		print(next.port,": encerrou a conexão")
		ind = self.intr.existeUser(next.nome)
		if ind != -1 : self.intr.delNode(ind)
		
	# servidor broadcast
	def broadcast(self,jsn):
		if not self.tipo :
			for on in self.online:
				on.send(jsn)
	
if __name__ == "__main__":
	print("digite 0 para servidor ou 1 para cliente")
	a = int(input())
	c = Node()
	if a == 0 :
		c.servidor()
	else:
		c.cliente()
		while 1:
			c.next.send(input())

		
