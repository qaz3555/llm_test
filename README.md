# llm_test
RUN find / -type f -exec grep -Il "python3.8" {} \; | xargs sed -i 's/python3\.8/python/g' || true
