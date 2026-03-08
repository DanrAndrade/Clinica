from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

# ==========================================
# CONSTANTES E ESCOLHAS (CHOICES)
# ==========================================

ROLE_CHOICES = (
    ('Admin', 'Admin'),
    ('Medico', 'Médico'),
    ('Recepcao', 'Recepção'),
    ('Laboratorio', 'Laboratório'),
)

STATUS_AGENDAMENTO_CHOICES = (
    ('Agendado', 'Agendado'),
    ('Confirmado', 'Confirmado'),
    ('NaRecepcao', 'Na Recepção'),
    ('EmAtendimento', 'Em Atendimento'),
    ('Finalizado', 'Finalizado'),
    ('Cancelado', 'Cancelado'),
    ('Faltou', 'Faltou'),
)

TIPO_AGENDAMENTO_CHOICES = (
    ('Presencial', 'Presencial'),
    ('Telemedicina', 'Telemedicina'),
)

TIPO_DOCUMENTO_CHOICES = (
    ('Evolucao', 'Evolução'),
    ('Receita', 'Receita'),
    ('Atestado', 'Atestado'),
)

STATUS_EXAME_CHOICES = (
    ('Pendente', 'Pendente'),
    ('Realizado', 'Realizado'),
    ('Recebido', 'Recebido'),
)

TIPO_ANEXO_CHOICES = (
    ('PDF', 'PDF'),
    ('Imagem', 'Imagem'),
    ('Laudo', 'Laudo'),
)

TIPO_TERMO_CHOICES = (
    ('Sintoma', 'Sintoma'),
    ('Queixa', 'Queixa'),
    ('Outros', 'Outros'),
)

STATUS_TRANSACAO_CHOICES = (
    ('Pago', 'Pago'),
    ('Pendente', 'Pendente'),
    ('Estornado', 'Estornado'),
)

STATUS_CONTA_CHOICES = (
    ('Pendente', 'Pendente'),
    ('Parcial', 'Parcial'),
    ('Pago', 'Pago'),
    ('Glosa', 'Glosa'),
    ('Cancelado', 'Cancelado'),
)

ACAO_LOG_CHOICES = (
    ('CREATE', 'CREATE'),
    ('UPDATE', 'UPDATE'),
    ('DELETE', 'DELETE'),
    ('VIEW', 'VIEW'),
)

# ==========================================
# 1. NÚCLEO E GESTÃO DE USUÁRIOS (RBAC)
# ==========================================

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome_completo, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, nome_completo=nome_completo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome_completo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nome_completo, password, **extra_fields)

class Clinica(models.Model):
    matriz = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='filiais')
    responsavel_tecnico = models.ForeignKey('Profissional', on_delete=models.SET_NULL, null=True, blank=True, related_name='clinicas_responsaveis')
    nome_fantasia = models.CharField(max_length=255)
    razao_social = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    cnes = models.CharField(max_length=20, blank=True, null=True)
    config_branding = models.JSONField(default=dict, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_fantasia

class Usuario(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome_completo']
    
    objects = UsuarioManager()

    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='colaboradores', null=True, blank=True)
    nome_completo = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Recepcao')
    is_active = models.BooleanField(default=True)
    google_calendar_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nome_completo

class Profissional(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='identidade_profissional')
    crm_numero = models.CharField(max_length=20, blank=True, null=True)
    crm_uf = models.CharField(max_length=2, blank=True, null=True)
    rqe = models.CharField(max_length=50, blank=True, null=True)
    conselho = models.CharField(max_length=20, choices=(('CRM', 'CRM'), ('CRO', 'CRO'), ('CRP', 'CRP')), default='CRM')
    assinatura_digital_b64 = models.TextField(blank=True, null=True)
    pix_chave = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.nome_completo} - {self.conselho}"

class ProfissionalClinica(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='vinculos_clinica')
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='corpo_clinico')
    ativo = models.BooleanField(default=True)
    data_vinculo_inicio = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profissional', 'clinica')

# ==========================================
# 2. PACIENTES E CONVÊNIOS
# ==========================================

class Paciente(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='pacientes')
    nome_completo = models.CharField(max_length=255)
    nome_mae = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    cns = models.CharField(max_length=20, blank=True, null=True)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=1, choices=(('M', 'M'), ('F', 'F'), ('O', 'O')))
    raca_cor = models.CharField(max_length=50, blank=True, null=True)
    nacionalidade = models.CharField(max_length=100, default='Brasileira')
    celular = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)
    alertas_alergias = models.JSONField(default=dict, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nome_completo

class Convenio(models.Model):
    nome = models.CharField(max_length=100)
    registro_ans = models.CharField(max_length=50, unique=True, blank=True, null=True)
    razao_social = models.CharField(max_length=255, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class CarteiraConvenio(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='planos')
    convenio = models.ForeignKey(Convenio, on_delete=models.CASCADE)
    numero_carteira = models.CharField(max_length=50, unique=True)
    plano = models.CharField(max_length=100, blank=True, null=True)
    validade_inicio = models.DateField(blank=True, null=True)
    validade_fim = models.DateField(blank=True, null=True)
    titular_nome = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('paciente', 'convenio')

class Procedimento(models.Model):
    nome = models.CharField(max_length=255)
    codigo_tuss = models.CharField(max_length=20, unique=True, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class TabelaPreco(models.Model):
    convenio = models.ForeignKey(Convenio, on_delete=models.CASCADE, related_name='tabelas_preco')
    procedimento = models.ForeignKey(Procedimento, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    vigencia_inicio = models.DateField()
    vigencia_fim = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('convenio', 'procedimento')

# ==========================================
# 3. AGENDA E INFRAESTRUTURA
# ==========================================

class Sala(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    disponivel = models.BooleanField(default=True)

class Disponibilidade(models.Model):
    profissional_clinica = models.ForeignKey(ProfissionalClinica, on_delete=models.CASCADE)
    dia_semana = models.IntegerField(choices=((i, str(i)) for i in range(7)))
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    ativo = models.BooleanField(default=True)

class BloqueioAgenda(models.Model):
    profissional_clinica = models.ForeignKey(ProfissionalClinica, on_delete=models.CASCADE)
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    motivo = models.CharField(max_length=255)

class Agendamento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    profissional_clinica = models.ForeignKey(ProfissionalClinica, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.SET_NULL, null=True, blank=True)
    convenio = models.ForeignKey(Convenio, on_delete=models.SET_NULL, null=True, blank=True)
    data_hora = models.DateTimeField(db_index=True)
    duracao_minutos = models.IntegerField(default=30)
    status = models.CharField(max_length=50, choices=STATUS_AGENDAMENTO_CHOICES, default='Agendado')
    tipo = models.CharField(max_length=50, choices=TIPO_AGENDAMENTO_CHOICES, default='Presencial')
    meeting_link = models.URLField(blank=True, null=True)
    motivo_cancelamento = models.TextField(blank=True, null=True)
    checkin_status = models.CharField(max_length=50, default='Pendente')
    deleted_at = models.DateTimeField(null=True, blank=True)

class AgendamentoProcedimento(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name='itens_faturamento')
    procedimento = models.ForeignKey(Procedimento, on_delete=models.CASCADE)
    valor_aplicado = models.DecimalField(max_digits=10, decimal_places=2)

class StatusHistory(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name='historico_status')
    status_anterior = models.CharField(max_length=50, choices=STATUS_AGENDAMENTO_CHOICES)
    status_novo = models.CharField(max_length=50, choices=STATUS_AGENDAMENTO_CHOICES)
    data_hora = models.DateTimeField(auto_now_add=True)
    alterado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

class NotificacaoLog(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    conteudo = models.TextField()
    status = models.CharField(max_length=50)
    data_envio = models.DateTimeField(auto_now_add=True)

# ==========================================
# 4. PRONTUÁRIO ELETRÔNICO (PEP)
# ==========================================

class Cid10(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    descricao = models.TextField()

class DocumentoClinico(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name='documentos')
    profissional = models.ForeignKey(Profissional, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=50, choices=TIPO_DOCUMENTO_CHOICES)
    dados_estruturados = models.JSONField(default=dict, blank=True)
    texto_rico_html = models.TextField(blank=True, null=True)
    cid_10 = models.ForeignKey(Cid10, on_delete=models.SET_NULL, null=True, blank=True)
    hash_integridade = models.CharField(max_length=255, blank=True, null=True)
    versao = models.IntegerField(default=1)
    assinado_digitalmente = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)

class SinaisVitais(models.Model):
    documento = models.ForeignKey(DocumentoClinico, on_delete=models.CASCADE, related_name='sinais_vitais')
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    pressao_arterial = models.CharField(max_length=20, null=True, blank=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    frequencia_cardiaca = models.IntegerField(null=True, blank=True)
    frequencia_respiratoria = models.IntegerField(null=True, blank=True)
    saturacao_o2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    glicemia = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    medido_em = models.DateTimeField(auto_now_add=True)

class PrescricaoItem(models.Model):
    documento = models.ForeignKey(DocumentoClinico, on_delete=models.CASCADE, related_name='itens_receita')
    medicamento = models.CharField(max_length=255)
    posologia = models.TextField()
    duracao = models.CharField(max_length=100, blank=True, null=True)
    alerta_interacao = models.TextField(blank=True, null=True)

class Laboratorio(models.Model):
    nome = models.CharField(max_length=255)
    token_api = models.CharField(max_length=255, blank=True, null=True)
    ativo = models.BooleanField(default=True)

class ExameItem(models.Model):
    documento = models.ForeignKey(DocumentoClinico, on_delete=models.CASCADE, related_name='pedidos_lab')
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.SET_NULL, null=True, blank=True)
    nome_exame = models.CharField(max_length=255)
    codigo_tuss = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_EXAME_CHOICES, default='Pendente')
    url_laudo_pdf = models.URLField(blank=True, null=True)

class Anexo(models.Model):
    documento = models.ForeignKey(DocumentoClinico, on_delete=models.CASCADE, related_name='anexos')
    tipo = models.CharField(max_length=50, choices=TIPO_ANEXO_CHOICES)
    url_arquivo = models.URLField()
    upload_em = models.DateTimeField(auto_now_add=True)

class TemplatePep(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    estrutura = models.JSONField(default=dict)

class TermoClinico(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    termo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=TIPO_TERMO_CHOICES)

class KitExame(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)

class ItemKitExame(models.Model):
    kit_exame = models.ForeignKey(KitExame, on_delete=models.CASCADE, related_name='itens')
    procedimento = models.ForeignKey(Procedimento, on_delete=models.CASCADE)

# ==========================================
# 5. MOTOR FINANCEIRO E TISS
# ==========================================

class LoteTiss(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    convenio = models.ForeignKey(Convenio, on_delete=models.CASCADE)
    numero_lote = models.CharField(max_length=100)
    xml_gerado = models.TextField()
    status_envio = models.CharField(max_length=50, default='Aberto')
    data_geracao = models.DateTimeField(auto_now_add=True)
    data_envio = models.DateTimeField(null=True, blank=True)

class ContaReceber(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.SET_NULL, null=True, blank=True)
    lote_tiss = models.ForeignKey(LoteTiss, on_delete=models.SET_NULL, null=True, blank=True)
    convenio = models.ForeignKey(Convenio, on_delete=models.SET_NULL, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_glosado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_vencimento = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CONTA_CHOICES, default='Pendente')
    glosa_motivo = models.TextField(blank=True, null=True)

class Transacao(models.Model):
    conta_receber = models.ForeignKey(ContaReceber, on_delete=models.CASCADE, related_name='transacoes')
    valor_bruto = models.DecimalField(max_digits=10, decimal_places=2)
    taxa_clinica = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_liquido = models.DecimalField(max_digits=10, decimal_places=2)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=50)
    data_pagamento = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=50, choices=STATUS_TRANSACAO_CHOICES, default='Pago')
    observacao = models.TextField(blank=True, null=True)

class RegraRepasse(models.Model):
    profissional_clinica = models.ForeignKey(ProfissionalClinica, on_delete=models.CASCADE)
    procedimento = models.ForeignKey(Procedimento, on_delete=models.CASCADE)
    percentual_clinica = models.DecimalField(max_digits=5, decimal_places=2)
    percentual_medico = models.DecimalField(max_digits=5, decimal_places=2)
    vigencia_inicio = models.DateField()

# ==========================================
# 6. LGPD E AUDITORIA
# ==========================================

class ConsentimentoLgpd(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    finalidade = models.CharField(max_length=255)
    aceito = models.BooleanField(default=False)
    data_assinatura = models.DateTimeField(auto_now_add=True)
    ip_origem = models.GenericIPAddressField(null=True, blank=True)

class LogAuditoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=50, choices=ACAO_LOG_CHOICES)
    tabela = models.CharField(max_length=100)
    recurso_id = models.IntegerField()
    dados_diff = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_origem = models.GenericIPAddressField(null=True, blank=True)