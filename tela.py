import tkinter as tk
import node
import json
import _thread

# ----------------------------------------------------------------------------
# gerencia todas as telas do sistema
class Aplicativo(tk.Tk):
	
	# valores iniciais da aplicação
	def __init__(self,interno,inicio = None):
		tk.Tk.__init__(self)
		self.tela_atual = None
		self.intr = interno
		if not inicio : inicio = Login
		self.trocarTela(inicio)
	# função que permite que as telas sejam alteradas
	def trocarTela(self, classe_tela):
		prox_tela = classe_tela(self)
		if self.tela_atual != None :
			self.tela_atual.destroy()
		self.tela_atual = prox_tela
		self.tela_atual.pack()



# ----------------------------------------------------------------------------
# aqui está os códigos da tela de login
# que é a tela inicial do cliente
class Login(tk.Frame):
	
	# codigos para gerar a tela:
	def __init__(self,master):
		self.master = master
		tk.Frame.__init__(self,master)
		# divisões do layout (linhas)
		f1 = tk.Frame(self) ; f1.pack()
		f2 = tk.Frame(self); f2.pack()
		f3 = tk.Frame(self); f3.pack()
		# primeira linha
		tk.Label(f1,text="IP do servidor:").pack( side = tk.LEFT)
		self.ip = tk.Entry(f1,width=10); self.ip.pack(side = tk.LEFT)
		tk.Label(f1,text="Porta:").pack( side = tk.LEFT )
		self.porta = tk.Entry(f1,width=5); self.porta.pack(side = tk.LEFT)
		# segunda linha
		tk.Label(f2,text="Nome:").pack( side = tk.LEFT)
		self.nome = tk.Entry(f2,width="27"); self.nome.pack()
		# terceira linha
		tk.Button(f3,text="Logar no sistema",
		command=self.logarNoSistema).pack()
	
	# procedimento do botão "logar no sistema"
	def logarNoSistema(self):
		dados = self.getDados()
		intr = self.master.intr
		
		# verifica se os dados estão ok
		if(not dados):
			print("verifique se os dados estão preenchidos corretamente")
			return False
		
		# tentativa de conectar ao servidor
		# apenas se ainda não tiver conectado
		if not intr.no:
			intr.no = node.Node(dados[0],dados[1],dados[2])
		else:
		# caso já esteja conectado, apenas tenta fazer login de outra forma
			intr.no.host = dados[0]
			intr.no.port = dados[1]
			intr.no.nome = dados[2]
		intr.no.cliente(intr)
		# tentando logar no o servidor
		#print(intr.no.next.nome)
		intr.no.next.send(intr.no.next.msg.login(intr.no.next))
		#intr.no.next.send(intr.no.next.msg.login(intr.no))
		
		
	# obtém os dados dos campos preenchidos
	# retorna 0 caso encontre algo de errado com os dados
	def getDados(self):
		try: dados = [self.ip.get(),int(self.porta.get()),self.nome.get()]
		except: dados = 0
		return dados

# ----------------------------------------------------------------------------
# aqui está os códigos referentes a segunda tela
class Menu(tk.Frame):
	
	def __init__(self,master):
		self.master = master
		self.frame = tk.Frame.__init__(self,master,width=300)
		self.label = tk.Label(self.frame,text="Exibindo lista de clientes")
		self.label.pack()
		self.lb = []
		self.entradas = []
		self.reload()
		self.conversa = " "

	
	
	def reload(self):
	
		for i in self.entradas:
			i.pack_forget()
		
		self.nomes = [i.nome for i in self.master.intr.no.online]
		if not self.nomes : self.nomes = ["ninguem"]
		self.var = tk.StringVar()
		self.var.set(self.nomes[0])
		def exemplo(nome):
			self.mostra_msg(nome,"")
		self.conversa = self.var
		self.op = tk.OptionMenu(self, self.var, *self.nomes, command = exemplo)
		self.op.pack()
		
		txt = tk.Entry(self)
		txt.pack()

		def enviarMsg():
			intr = self.master.intr
			print("enviando msg ",txt.get(),"para: ", self.var.get())
			intr.no.next.send(intr.no.next.msg.chatMsg(self.var.get(),intr.no.nome,txt.get()))
		btn = tk.Button(self, text = "enviar", command = enviarMsg)
		btn.pack()
		self.entradas=[self.op,txt,btn]
		#self.lb.append(txt)
		#self.lb.append(btn)
		#self.lb.append(op)

	def mostra_msg(self, remetente, destinatario):

		while len(self.lb):
			i = self.lb.pop()
			i.pack_forget()

		intr = self.master.intr
		# critical
		l = [ i.nome for i in self.master.intr.no.online]
		l = l.index(remetente)
		l = self.master.intr.no.online[l]
		print("lista",l.msgChat)
		for i in  l.msgChat:
			t = tk.Label(self.frame, text =  i[1] + " : "  + i[0])
			t.pack()
			self.lb.append(t)

	def reset(self):
		self.master.intr.no = None
		self.label.pack_forget()
		self.nomes.clear()
		self.var.set("")
		self.op['menu'].delete(0, tk.END)
		while len(self.lb):
			i = self.lb.pop()
			i.pack_forget()
			
			

class TelaInicioServidor(tk.Frame):
	def __init__(self, master):
		self.master = master
		self.frame = tk.Frame.__init__(self, master, width = 500)
		f1 = tk.Frame(self)
		f1.pack()
		f2 = tk.Frame(self)
		f2.pack()

		def criarServidor():
				self.master.intr.no = node.Node("",int(self.porta.get()))
				self.master.intr.no.servidor(self.master.intr)
				
				

		def criarTreadServidor():
			_thread.start_new_thread(criarServidor,())
			
			

		tk.Label(f1, text = "porta ", relief = tk.RIDGE, width = 10).pack(side = tk.LEFT)
		self.porta = tk.Entry(f1, relief = tk.SUNKEN, width = 20)
		self.porta.pack(side = tk.RIGHT)
		btn = tk.Button(f2, text = "criar servidor", command = criarTreadServidor)
		btn.pack()

class TelaServidor(tk.Frame):
	def __init__(self, master):
		self.master = master
		self.frame = tk.Frame.__init__(self, master)
		self.lb = []
		self.f1 = tk.Frame(self)
		self.f1.pack()
		self.f2 = tk.Frame(self)
		self.f2.pack()
		
		#tk.Label(self.f1, text = "clientes logados: ").pack(side = tk.LEFT, anchor = 's')
		self.listboxUsuarios = tk.Listbox(self.f2)
		self.listboxUsuarios.pack(side = tk.LEFT)
		self.listboxUsuarios.insert(tk.END, "clientes logados")
		self.listboxUsuarios.config(height = 30)
		
		
		#tk.Label(self.f1, text = "log do servidor").pack(side = tk.RIGHT, anchor = 'w')
		self.listboxLog = tk.Listbox(self.f2)
		self.listboxLog.pack(side = tk.RIGHT)
		self.listboxLog.insert(tk.END, "log do sistema")
		self.listboxLog.config(width = 80, height = 30)

	def reload(self, msg = 0, tipo = 0):
		if msg:
			self.listboxLog.insert(tk.END, tipo +  msg)
			#self.listboxLog.insert(tk.END,)

		#self.listboxUsuarios.pack_forget()
		self.listboxUsuarios.delete(1, tk.END)
		for i in self.master.intr.no.online :
			self.listboxUsuarios.insert(tk.END, i.nome)
			#self.listboxUsuarios.pack(side = tk.LEFT)
			
		#self.listboxUsuarios.pack(side = tk.LEFT)
			


		

	
		

			
		
		
	
	#def add_label(self):
	#	nb = tk.Label(self,text="nova "+str(len(self.lb))); nb.pack()
	#	self.lb.append(nb)
	
	#def rm_label(self):
	#	if(len(self.lb)):
	#		a = self.lb.pop(0)
	#		a.pack_forget()
	

# app = Aplicativo()
# app.mainloop()

		
