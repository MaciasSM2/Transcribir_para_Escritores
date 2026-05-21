import { ISpeechTranscriber, SpeechTranscriberEvents } from './ISpeechTranscriber';

// ---------------------------------------------------------------------------
// Interfaces de la Web Speech API del navegador.
// No existe un paquete @types/ oficial y estable para estas APIs; definirlas
// localmente es la práctica correcta para mantener tipado estricto.
// ---------------------------------------------------------------------------

interface SpeechRecognitionResultItem {
  readonly transcript: string;
  readonly confidence: number;
}

interface SpeechRecognitionResult {
  readonly isFinal: boolean;
  readonly length: number;
  [index: number]: SpeechRecognitionResultItem;
}

interface SpeechRecognitionResultList {
  readonly length: number;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number;
  readonly results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  readonly error: string;
  readonly message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onresult: ((ev: SpeechRecognitionEvent) => void) | null;
  onerror: ((ev: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognition;
}

// Extensión del tipo Window para incluir las variantes vendor-prefixed
interface SpeechRecognitionWindow extends Window {
  SpeechRecognition?: SpeechRecognitionConstructor;
  webkitSpeechRecognition?: SpeechRecognitionConstructor;
}

// ---------------------------------------------------------------------------

export class BrowserSpeechAdapter implements ISpeechTranscriber {
  private recognition: SpeechRecognition | null = null;
  private isRecording: boolean = false;
  private isManualStop: boolean = true;
  private events: Partial<SpeechTranscriberEvents> = {};
  private lang: string;

  constructor(lang: string = 'es-ES') {
    this.lang = lang;
  }

  private initRecognition(): boolean {
    if (typeof window === 'undefined') return false;

    const win = window as SpeechRecognitionWindow;
    const SpeechRecognitionClass = win.SpeechRecognition ?? win.webkitSpeechRecognition;

    if (!SpeechRecognitionClass) {
      console.warn('Web Speech API no está soportada en este navegador.');
      return false;
    }

    this.recognition = new SpeechRecognitionClass();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = this.lang;

    this.recognition.onresult = this.handleResult.bind(this);
    this.recognition.onerror = this.handleError.bind(this);
    this.recognition.onend = this.handleEnd.bind(this);

    return true;
  }

  private handleResult(event: SpeechRecognitionEvent): void {
    let final = '';
    let interim = '';

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) final += event.results[i][0].transcript;
      else interim += event.results[i][0].transcript;
    }

    // El espacio extra asegura que las frases no se peguen
    if (final && this.events.onFinalResult) this.events.onFinalResult(final + ' ');
    if (this.events.onInterimResult) this.events.onInterimResult(interim);
  }

  private handleError(event: SpeechRecognitionErrorEvent): void {
    if (this.events.onError) this.events.onError(event.error);
    if (event.error === 'not-allowed') this.updateStatus(false);
  }

  private handleEnd(): void {
    // Auto-reinicio solo si: el usuario NO ha pulsado Parar (isManualStop=false)
    // Y el estado interno confirma que seguimos en sesión activa (isRecording=true).
    // La doble guarda evita reinicios fantasma de eventos 'end' retrasados que
    // llegan después de que stop() ya había actualizado el estado.
    if (!this.isManualStop && this.isRecording) {
      try {
        this.recognition?.start();
      } catch (e) {
        console.warn('Error al auto-reiniciar el reconocimiento', e);
        this.updateStatus(false);
      }
    } else {
      this.updateStatus(false);
    }
  }

  private updateStatus(status: boolean): void {
    this.isRecording = status;
    if (this.events.onStatusChange) this.events.onStatusChange(status);
  }

  public subscribe(events: Partial<SpeechTranscriberEvents>): void {
    this.events = events;
  }

  public unsubscribe(): void {
    this.events = {};
  }

  public start(): void {
    this.isManualStop = false;

    if (!this.recognition) {
      const initialized = this.initRecognition();
      if (!initialized) return; // Navegador no soportado
    }

    try {
      this.recognition!.start();
      this.updateStatus(true);
    } catch (e) {
      console.warn('Speech recognition ya está iniciado o falló al iniciar.', e);
    }
  }

  public stop(): void {
    this.isManualStop = true;
    if (!this.recognition) return;

    try {
      this.recognition.stop();
      this.updateStatus(false);
    } catch (e) {
      console.warn('Error al detener el reconocimiento de voz', e);
    }
  }
}
