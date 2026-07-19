import { Play, Send } from "lucide-react";

interface HiringRequestFormProps {
  value: string;
  isLoading: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

const examples = [
  {
    label: "使用新加坡示例",
    value: "我想在新加坡雇一名月薪 8000 SGD 的高级工程师，10 月入职"
  },
  {
    label: "使用越南冲突示例",
    value: "我想在越南雇一名月薪 40000000 VND 的工程师，试用期 6 个月，年假 10 天"
  },
  {
    label: "使用多国对比示例",
    value: "在新加坡和越南雇同样的人，月薪 8000，哪个成本低？"
  }
];

export function HiringRequestForm({
  value,
  isLoading,
  onChange,
  onSubmit
}: HiringRequestFormProps) {
  return (
    <section className="request-panel" aria-labelledby="request-title">
      <div>
        <p className="eyebrow">Global Employment Agent</p>
        <h1 id="request-title">全球雇佣方案生成器</h1>
      </div>
      <label htmlFor="hiring-request">雇佣需求</label>
      <textarea
        id="hiring-request"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="例如：我想在新加坡雇一名月薪 8000 SGD 的高级工程师，10 月入职"
        rows={5}
      />
      <div className="example-row">
        {examples.map((example) => (
          <button
            key={example.label}
            type="button"
            className="secondary-button"
            onClick={() => onChange(example.value)}
          >
            <Play aria-hidden="true" size={16} />
            {example.label}
          </button>
        ))}
      </div>
      <button type="button" className="primary-button" disabled={isLoading} onClick={onSubmit}>
        <Send aria-hidden="true" size={18} />
        {isLoading ? "生成中" : "生成雇佣方案"}
      </button>
    </section>
  );
}

