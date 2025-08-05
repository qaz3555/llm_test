# llm_test
RUN find / -type f -exec grep -Il "python3.8" {} \; | xargs sed -i 's/python3\.8/python/g' || true

RUN for dir in /usr/lib /usr/share /usr/include /usr/local; do \
      find "$dir" -type f -exec grep -Il "python3.8" {} \; \
      | xargs sed -i 's/python3\.8/python/g' || true; \
    done
