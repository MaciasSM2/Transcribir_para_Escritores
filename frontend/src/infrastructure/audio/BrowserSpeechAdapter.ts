// frontend/src/infrastructure/audio/BrowserSpeechAdapter.ts
import { ISpeechTranscriber, TranscriptionCallbacks } from './ISpeechTranscriber';

export class BrowserSpeechAdapter implements ISpeechTranscriber {
  private recognition: any | null = null;
  private callbacks: TranscriptionCallbacks | null = null;
  private isRunning: boolean = false;
  private isIntentionalStop: boolean = false;
  
  // Guardamos el índice del último resultado consolidado para calcular deltas puras
  private lastResultIndex: number = 0;

  public initialize(callbacks: TranscriptionCallbacks): void {
    this.callbacks = callbacks;
    
    // Verificación de soporte nativo en el agente de usuario
    const SpeechClass = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechClass) {
      throw new Error('Web Speech API no es compatible con este navegador.');
    }

    this.recognition = new SpeechClass();
    
    // CONFIGURACIÓN CRÍTICA PARA EVITAR EL DESFASE:
    this.recognition.continuous = true;      // No se detiene al procesar una frase completa
    this.recognition.interimResults = true;  // Despacha resultados en tiempo real para previsualización
    this.recognition.lang = 'es-MX';         // Configuración idiomática regional estándar
    
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    if (!this.recognition || !this.callbacks) return;

    this.recognition.onresult = (event: any) => {
      let interimTranscript = '';
      let deltaTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const result = event.results[i];
        if (result.isFinal) {
          // Extraemos la delta consolidada sin tocar la historia anterior
          deltaTranscript += result[0].transcript;
          // Actualizamos nuestro puntero de control de segmentación
          this.lastResultIndex = i + 1;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      // Despachamos los resultados a través de los canales correspondientes
      if (deltaTranscript.length > 0 && this.callbacks) {
        this.callbacks.onDeltaResult(this.sanitizeChunk(deltaTranscript));
      }
      if (this.callbacks) {
        this.callbacks.onInterimResult(interimTranscript);
      }
    };

    this.recognition.onerror = (event: any) => {
      if (event.error === 'no-speech') return; // Mitigación silenciosa de pausas largas
      if (this.callbacks) this.callbacks.onError(`Speech Error: ${event.error}`);
    };

    this.recognition.onend = () => {
      // MECANISMO DE DOBLE GUARDIA: Si el navegador apaga el micro por inactividad
      // pero el escritor no ha presionado "Stop", reanudamos instantáneamente.
      if (!this.isIntentionalStop && this.isRunning) {
        setTimeout(() => {
          try {
            this.recognition.start();
          } catch (e) {
            // Protección contra intentos de doble inicio síncronos
          }
        }, 80); // Microsegundos de delay seguros para liberar la tarjeta de sonido
      } else {
        this.isRunning = false;
        if (this.callbacks) this.callbacks.onDisconnect();
      }
    };
  }

  public start(): void {
    if (!this.recognition || this.isRunning) return;
    this.isRunning = true;
    this.isIntentionalStop = false;
    this.lastResultIndex = 0;
    this.recognition.start();
  }

  public stop(): void {
    if (!this.recognition || !this.isRunning) return;
    this.isIntentionalStop = true;
    this.isRunning = false;
    this.recognition.stop();
  }

  public isActive(): boolean {
    return this.isRunning;
  }

  /**
   * Asegura que el fragmento entrante no contenga espacios duplicados en los extremos.
   */
  private sanitizeChunk(text: string): string {
    return text.replace(/\s+/g, ' ');
  }
}
