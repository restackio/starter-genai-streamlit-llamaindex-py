# GenAI Starter - Llamaindex - Restack

An example of how to deploy a [LangChain](https://www.llamaindex.ai/) application with [Streamlit](https://streamlit.io/) with Restack.

---

### Environment Variables

<details>

<summary>ℹ️ OpenAI models</summary>

In this example, we chose OpenAI's models for the sake of simplicity, but you're free to choose the models you prefer as LangChain provides support for other models as well. In that case, we recommend you remove the `OPENAI_API_KEY` environment variable and the relevant application code.

</details>

To ensure your successful deployment, set the following environment variables:

```bash
# Get it from https://platform.openai.com/account/api-keys
OPENAI_API_KEY=<YOUR_API_KEY>
```
