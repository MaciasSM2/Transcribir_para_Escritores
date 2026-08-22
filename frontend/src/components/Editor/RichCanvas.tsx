import React, { useRef } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { TextStyle } from '@tiptap/extension-text-style';
import Color from '@tiptap/extension-color';
import FontFamily from '@tiptap/extension-font-family';
import TextAlign from '@tiptap/extension-text-align';
import CharacterCount from '@tiptap/extension-character-count';
import { Extension } from '@tiptap/core';
import { useUIStore } from '@/store/useUIStore';
import { useDictationStore } from '@/store/useDictationStore';
import { BubbleMenu } from './BubbleMenu';
import { Toolbar } from './Toolbar';
import { useDialogueTransform } from '../../infrastructure/editor/commands/useDialogueTransform';
import { SnapshotShortcuts } from '../../infrastructure/editor/Shortcuts';
import { useProjectStore } from '../../store/useProjectStore';
import { useInferenceStore } from '../../store/useInferenceStore';
import { useAutoSave } from '../../hooks/useAutoSave';
import { LocalPersistenceService } from '../../infrastructure/storage/LocalPersistenceService';
import { useEffect } from 'react';
import { Mic, MicOff, Terminal, Sparkles } from 'lucide-react';
import { useCleanDictation } from '../../hooks/useCleanDictation';
import { LiveTranscriptionBuffer } from '../Panels/LiveTranscriptionBuffer';
import Highlight from '@tiptap/extension-highlight';
import { diffWords } from 'diff';
export const RichCanvas = () => {
  const { editorTheme } = useUIStore();
  const { documentText, setDocumentText, lastDictatedChunk, setLastDictatedChunk, isRecording, isProcessingAudio } = useDictationStore();
  const { activeChapterId } = useProjectStore();
  const { startRecording, stopRecording } = useCleanDictation();
  const transformRef = useRef<((toneName: string) => void) | undefined>(undefined);
  
  const isProgrammaticRef = useRef(false);

  const setContentProgrammatic = (content: string) => {
    if (!editor) return;
    isProgrammaticRef.current = true;
    editor.commands.setContent(content);
    setTimeout(() => {
      isProgrammaticRef.current = false;
    }, 50);
  };

  const editor = useEditor({
    extensions: [
      StarterKit, 
      TextStyle, 
      Color,
      FontFamily,
      CharacterCount,
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      Extension.create({
        name: 'dialogueShortcuts',
        addKeyboardShortcuts() {
          return {
            'Mod-Shift-d': () => {
              if (transformRef.current) {
                transformRef.current('Narrativa Estándar');
              }
              return true;
            },
          };
        },
      }),
      SnapshotShortcuts,
      Highlight.configure({
        HTMLAttributes: {
          class: 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 rounded px-1 font-semibold mx-0.5',
        },
      }),
    ],
    content: documentText || `<h2>Capítulo 1: El Comienzo</h2><p>Escribe o dicta tu historia aquí...</p>`,
    immediatelyRender: false,
    onUpdate: ({ editor }) => {
      setDocumentText(editor.getHTML());
      
      // Si el usuario escribe o dicta manualmente, finalizamos la comparación para no pisar sus cambios
      if (!isProgrammaticRef.current) {
        const currentLiveBuffer = useInferenceStore.getState().liveBuffer;
        if (currentLiveBuffer) {
          useInferenceStore.getState().clearLog();
          setShowingCorrections(false);
        }
      }
    },
    editorProps: {
      attributes: {
        class: 'prose prose-slate prose-lg max-w-none focus:outline-none font-serif text-slate-800',
      },
    },
  });

  const { transformSelectedText } = useDialogueTransform(editor);
  transformRef.current = transformSelectedText;

  // Sincronización Fase C: Cargar contenido del capítulo activo
  useEffect(() => {
    if (!editor || !activeChapterId) return;
    
    const loadContent = async () => {
      const content = await LocalPersistenceService.getLatestContent(activeChapterId.toString());
      if (content) {
        setContentProgrammatic(content);
      } else {
        setContentProgrammatic(`<h2>Nuevo Capítulo</h2><p>Comienza a escribir...</p>`);
      }
    };
    
    loadContent();
  }, [editor, activeChapterId]);

  // Sincronización Fase C: Insertar dictado en el lienzo nativamente o ejecutar comandos de voz
  useEffect(() => {
    if (!editor || !lastDictatedChunk) return;
    
    // 1. Interceptar comandos de voz (Filtro Local)
    import('../../infrastructure/editor/VoiceCommandHandler').then(({ handleVoiceCommand }) => {
      const isCommand = handleVoiceCommand(editor, lastDictatedChunk);
      
      // 2. Si no es un comando, inyectar el texto normal
      if (!isCommand) {
        // Heurística de espaciado: Si el cursor no está al inicio, agregar un espacio
        const textToInsert = ` ${lastDictatedChunk.trim()}`;
        editor.chain().focus().insertContent(textToInsert).run();
      }
      
      setLastDictatedChunk(''); // Limpiar para el próximo chunk
    });
  }, [editor, lastDictatedChunk, setLastDictatedChunk]);

  // Hook de Auto Guardado
  useAutoSave(editor, activeChapterId ? activeChapterId.toString() : '');

  const { pendingReplacement, setPendingReplacement, liveBuffer, isProcessing } = useInferenceStore();
  const [showingCorrections, setShowingCorrections] = React.useState(false);
  const originalPlainRef = useRef<string>('');
  const originalHtmlRef = useRef<string>('');
  const highlightedHtmlRef = useRef<string>('');

  const stripHtml = (html: string) => {
    if (typeof window === 'undefined') return html;
    const doc = new DOMParser().parseFromString(html, 'text/html');
    return doc.body.textContent || '';
  };

  const generateHighlightedHtml = (originalHtml: string, correctedHtml: string) => {
    const originalPlain = stripHtml(originalHtml);
    const correctedPlain = stripHtml(correctedHtml);
    const diffResult = diffWords(originalPlain, correctedPlain);
    let html = '';
    
    const escapedValue = (val: string) => {
      return val
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br/>');
    };

    html += '<p>';
    diffResult.forEach((chunk) => {
      if (chunk.removed) {
        return;
      }
      if (chunk.added) {
        html += `<mark>${escapedValue(chunk.value)}</mark>`;
      } else {
        html += escapedValue(chunk.value);
      }
    });
    html += '</p>';
    
    return html.replace(/<p><\/p>/g, '');
  };

  // Escuchar inicio de procesamiento para capturar el original
  useEffect(() => {
    if (isProcessing && editor) {
      originalPlainRef.current = editor.getText();
      originalHtmlRef.current = editor.getHTML();
    }
  }, [isProcessing, editor]);

  // Escuchar fin de procesamiento de estilo para autoseleccionar la corrección y activar el toggle
  useEffect(() => {
    if (!isProcessing && liveBuffer && editor) {
      const html = generateHighlightedHtml(originalHtmlRef.current, liveBuffer);
      highlightedHtmlRef.current = html;
      setShowingCorrections(true);
      setContentProgrammatic(html);
    }
  }, [isProcessing, liveBuffer, editor]);

  // Sincronización de limpieza de la IA
  useEffect(() => {
    if (!liveBuffer) {
      setShowingCorrections(false);
    }
  }, [liveBuffer]);

  // Sincronización Fase 3: Mesa de Revisión (Aplicar Sugerencia)
  useEffect(() => {
    if (pendingReplacement && editor) {
      // En un caso real, buscaríamos la posición exacta. Por ahora, reemplazo de texto simple.
      const currentHtml = editor.getHTML();
      if (currentHtml.includes(pendingReplacement.original)) {
        const newHtml = currentHtml.replace(pendingReplacement.original, pendingReplacement.replaced);
        setContentProgrammatic(newHtml);
      }
      setPendingReplacement(null);
    }
  }, [pendingReplacement, editor, setPendingReplacement]);

  // Drag logic para la caja flotante
  const [dragPos, setDragPos] = React.useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = React.useState(false);
  const [isAnchored, setIsAnchored] = React.useState(true);
  const dragStart = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || isAnchored) return;
      setDragPos({
        x: e.clientX - dragStart.current.x,
        y: e.clientY - dragStart.current.y
      });
    };
    const handleMouseUp = () => setIsDragging(false);

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, isAnchored]);

  const onMouseDown = (e: React.MouseEvent) => {
    if (isAnchored) return;
    setIsDragging(true);
    dragStart.current = {
      x: e.clientX - dragPos.x,
      y: e.clientY - dragPos.y
    };
  };

  return (
    <div className="flex-1 h-full bg-slate-100 dark:bg-slate-950 relative flex flex-col overflow-hidden">
      
      {/* BOTÓN FLOTANTE PARA COMPARAR VERSIONES (ORIGINAL VS IA) */}
      {editor && liveBuffer && !isProcessing && (
        <div className="absolute top-4 right-4 z-40 flex items-center gap-2 animate-in fade-in slide-in-from-top-4 duration-300">
          <button
            onClick={() => {
              if (showingCorrections) {
                setContentProgrammatic(originalHtmlRef.current);
                setShowingCorrections(false);
              } else {
                setContentProgrammatic(highlightedHtmlRef.current);
                setShowingCorrections(true);
              }
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-wider transition-all duration-300 shadow-xl hover:scale-105 ${
              showingCorrections
                ? 'bg-purple-600 hover:bg-purple-700 text-white ring-2 ring-purple-300 dark:ring-purple-900'
                : 'bg-white hover:bg-slate-100 text-slate-800 border border-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 dark:text-slate-200 dark:border-slate-800'
            }`}
          >
            <Sparkles size={14} className={showingCorrections ? 'animate-pulse text-yellow-300' : 'text-purple-500'} />
            {showingCorrections ? 'Ver Original (Sin Cambios)' : 'Ver Estilo IA (Corregido)'}
          </button>
        </div>
      )}

      {/* CONTENEDOR DE ENFOQUE (EL "ESCRITORIO") */}
      <div className="flex-1 overflow-y-auto custom-scrollbar py-12 flex justify-center items-start pb-40">
        
        {/* EL FOLIO A4 (EL "PAPEL") */}
        <div className="w-[210mm] min-h-[297mm] bg-white dark:bg-white shadow-[0_0_50px_-12px_rgba(0,0,0,0.15)] dark:shadow-[0_0_60px_-15px_rgba(0,0,0,0.4)] border border-slate-200 dark:border-slate-800 p-[25mm] transition-all duration-500 ease-in-out relative">
          
          {editor && <BubbleMenu editor={editor} />}
          {editor && <Toolbar editor={editor} />}
          <EditorContent 
            editor={editor} 
            className="focus:outline-none mt-4"
          />
          
        </div>
      </div>

      {/* CAJA FLOTANTE DE DICTADO Y TRANSCRIPCIÓN EN VIVO */}
      <div 
        className={`${
          isAnchored 
            ? 'absolute bottom-0 left-0 w-full rounded-t-xl rounded-b-none border-x-0 border-b-0' 
            : 'fixed bottom-12 left-1/2 -translate-x-1/2 w-[600px] rounded-xl'
        } z-50 overflow-hidden flex flex-col bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-slate-800 shadow-2xl transition-all`}
        style={isAnchored ? { transform: 'none' } : { transform: `translate(calc(-50% + ${dragPos.x}px), ${dragPos.y}px)` }}
      >
        {/* Header / Botón de dictado */}
        <div 
          className={`p-3 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-950/50 ${isAnchored ? '' : 'cursor-move'}`}
          onMouseDown={onMouseDown}
        >
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
            <Terminal size={14} className="text-amber-500" />
            <span className="text-[10px] font-bold uppercase tracking-wider">
              Voz en Vivo {isAnchored ? '(Anclado)' : '(Arrastra para mover)'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); setIsAnchored(!isAnchored); }}
              className="px-2 py-1.5 text-[10px] font-medium text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 bg-slate-200/50 dark:bg-slate-800/50 rounded-lg transition-colors"
            >
              {isAnchored ? 'Desanclar' : 'Anclar abajo'}
            </button>
            {isRecording ? (
              <button 
                onClick={(e) => { e.stopPropagation(); stopRecording(); }}
                disabled={isProcessingAudio}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg transition-colors font-medium text-[10px] ${
                  isProcessingAudio
                    ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
                    : 'bg-red-100 text-red-600 hover:bg-red-200'
                }`}
              >
                <MicOff size={12} /> Pausar
              </button>
            ) : (
              <button 
                onClick={(e) => { e.stopPropagation(); startRecording(); }}
                disabled={isProcessingAudio}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg transition-colors font-medium text-[10px] ${
                  isProcessingAudio
                    ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                <Mic size={12} /> Dictar
              </button>
            )}
          </div>
        </div>
        {/* Buffer de Voz Viva */}
        <div className={`p-3 overflow-y-auto custom-scrollbar ${isAnchored ? 'h-32' : 'max-h-32'}`}>
          <LiveTranscriptionBuffer />
        </div>
      </div>

      {/* MARCADOR DE PÁGINA FLOTANTE (Opcional, estilo Word) */}
      <div className={`absolute left-1/2 -translate-x-1/2 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md px-4 py-2 rounded-full border border-slate-200 dark:border-slate-800 text-[10px] font-bold text-slate-400 shadow-sm z-50 transition-all duration-300 ${
        isAnchored ? 'bottom-48' : 'bottom-6'
      }`}>
        PÁGINA 1 | {editor?.storage.characterCount?.words() || 0} PALABRAS
      </div>
    </div>
  );
};
