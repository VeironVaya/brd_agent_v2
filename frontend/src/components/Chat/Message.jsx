import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

export default function Message({ message }) {


  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[74%] bg-text-primary rounded-[20px] px-4.5 py-3.5 text-base leading-relaxed text-white">
          {message.text}
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-1.5 items-start">
      <span className="text-[11px] font-semibold text-text-tertiary pl-1">BRD-Agent</span>
      <div className="max-w-[74%] bg-white shadow-[0_1px_2px_rgba(0,0,0,.05),0_1px_1px_rgba(0,0,0,.03)] rounded-[20px] px-4.5 py-3.5 text-base leading-relaxed markdown-body overflow-x-auto">
        <ReactMarkdown 
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
        >
          {message.text}
        </ReactMarkdown>
      </div>
    </div>
  )
}
