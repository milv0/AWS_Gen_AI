import os
import streamlit as st
import base64
import boto3
import json
import random

# AWS 리전 설정
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# 모델 ID 설정
MODEL_ID = "STABLE_DIFFUSION_MODEL_ID"

# Create a Bedrock Runtime client
client = boto3.client("bedrock-runtime", region_name="us-east-1")

def generate_image(prompt):
    # Generate a random seed
    seed = random.randint(0, 4294967295)

    # Format the request payload
    native_request = {
        "text_prompts": [{"text": prompt}],
        "style_preset": "photographic",
        "seed": seed,
        "cfg_scale": 10,
        "steps": 50,
    }

    # Convert the native request to JSON
    request = json.dumps(native_request)

    # Invoke the model with the request
    response = client.invoke_model(modelId=MODEL_ID, body=request)

    # Decode the response body
    model_response = json.loads(response["body"].read())

    # Extract the image data
    base64_image_data = model_response["artifacts"][0]["base64"]

    # Decode the base64 image data
    image_data = base64.b64decode(base64_image_data)

    return image_data

def main():
    st.set_page_config(page_title='🖼️ 이미지 생성', layout='wide')

    st.title("🖼️ 이미지 생성")

    st.page_link('https://papago.naver.com/', label='파파고', icon='📕')
    prompt = st.text_input("원하시는 이미지에 대한 설명을 적어주세요(영어로)")


    if st.button("Generate Image"):
        if prompt:
            try:
                image_data = generate_image(prompt)
                st.image(image_data, caption="Generated Image")
            except Exception as e:
                st.error(f"Error generating image: {e}")
        else:
            st.warning("Please enter an image description.")

if __name__ == "__main__":
    main()
