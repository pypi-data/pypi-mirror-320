# KSSDS

한국어 대화 시스템 용 문장 분리기

KSSDS는 한국어 대화 시스템을 다루기 위해 설계된 딥러닝 기반 문장 분리기입니다.

기존의 한국어 문장 분리기는 규칙 또는 통계 기반의 모델로, 종결 어미나 구두점에 크게 의존하는 경향이 있습니다.  
이러한 특성 때문에, STT(Speech-to-Text) 모델을 통해 생성된 텍스트에서 자주 발생하는 변칙적인 사례  
(예: 구두점 생략, 어순 도치 등)에 효과적으로 대응하기 어려운 한계가 있습니다.

KSSDS는 이러한 한계를 극복하기 위해 개발된 모델로,  
트랜스포머 기반 딥러닝을 활용하여 대화 시스템에서도 안정적이고 유연한 문장 분리를 목표로 합니다.

---

## 설치

To install KSSDS, simply use pip:

```bash
pip install KSSDS
```

---

## Quickstart

다음은 KSSDS를 사용하여 한국어 문장을 분리하는 간단한 예제입니다:

```python
from KSSDS import KSSDS

# Initialize the model
kssds = KSSDS()

# Split sentences
input_text = "안녕하세요. 오늘 날씨가 참 좋네요. 저는 산책을 나갈 예정입니다."
split_sentences = kssds.split_sentences(input_text)

# Print results
for idx, sentence in enumerate(split_sentences):
    print(f"{idx + 1}: {sentence}")
```

<pre style="background-color:#F5EDED; color:white; padding:10px; border-radius:5px; font-family:monospace;">
<span style="color:#a29acb;">1: 안녕하세요.</span>
<span style="color:#c3adad;">2: 오늘 날씨가 참 좋네요.</span>
<span style="color:YellowGreen;">3: 저는 산책을 나갈 예정입니다.</span>
</pre>

---

## 문서 및 자세한 정보

For advanced usage, training scripts, or contributing, please visit the [GitHub Repository](https://github.com/ggomarobot/KSSDS).